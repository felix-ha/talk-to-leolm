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
    
def ask_model(url_server: str, route_check:str, route_model: str, question: str, context: str):
    if server_is_online(url_server, route_check):
        payload = {'question': question, 'context': context}
        headers = {'content-type': 'application/json'}
        response = requests.post(f'{url_server}/{route_model}', data=json.dumps(payload), headers=headers)
        response = response.json()
        answer = response['answer'][0]['generated_text'].split('<|im_start|>assistant')[1].lstrip()
        return answer
    else:
        return "LLM ist offline!"


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
        assistant_response = answer = ask_model(url_server, route_check, route_model, prompt, context)

        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.15)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    