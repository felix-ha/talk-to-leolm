import os
import time
import requests
import json
import streamlit as st


ip_adress_server = os.getenv('IP_ADRESS_SERVER', 'localhost')
port = 5000
url_server = f'http://{ip_adress_server}:{port}'
route_check = '/up-status'
route_model = '/llm'


def server_is_online(url_server: str, route_check:str) -> bool:
    try:
      response = requests.get(f'{url_server}/{route_check}')
      if response.status_code == 200:
        return True
      else:
        return False
    except requests.exceptions.ConnectionError:
      return False
    
def ask_model(url_server: str, route_check:str, route_model: str, question: str, context: str, prompt_history: str):
    if server_is_online(url_server, route_check):
        payload = {'question': question, 'context': context, 'prompt': prompt_history}
        headers = {'content-type': 'application/json'}
        response = requests.post(f'{url_server}/{route_model}', data=json.dumps(payload), headers=headers)
        response = response.json()
        prompt_history = response['answer'][0]['generated_text']
        answer = prompt_history.split('<|im_start|>assistant')[1].lstrip()
        return answer, prompt_history
    else:
        return "LLM ist offline!", None


st.write("""
# Frag  LeoLM!
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Eingabe..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        context = None
        prompt_history = None
        if len(st.session_state.messages) > 2:
            prompt_history = st.session_state.messages[-2]['promt_history']
        assistant_response, prompt_history = ask_model(url_server, route_check, route_model, prompt, context, prompt_history)

        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.1)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response, "promt_history": prompt_history})
    print(st.session_state.messages)
