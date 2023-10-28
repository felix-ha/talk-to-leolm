import os
from pathlib import Path
import time
import requests
import json
import tempfile
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
    
def ask_model(url_server: str, route_check:str, route_model: str, question: str, context: str, prompt_history: str, path_to_upload=None):
    if server_is_online(url_server, route_check):
        payload = {'question': question, 'context': context, 'prompt': prompt_history}

        # Send file only at start of conversation
        if path_to_upload and prompt_history is None:
            prompt_history = None
            with open(path_to_upload, "rb") as f:
                file = {'file': f}
                response = requests.post(f'{url_server}/{route_model}', files=file, data=payload)
                response = response.json()
        else:
            headers = {'content-type': 'application/json'}
            response = requests.post(f'{url_server}/{route_model}', data=json.dumps(payload), headers=headers)
            response = response.json()

        prompt_history = response['answer'][0]['generated_text']
        answer = prompt_history.split('<|im_start|>assistant')[-1].lstrip()
        return answer, prompt_history
    else:
        return "LLM ist offline!", None



with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir_path = Path(tmpdir)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.write("""
    # Frag  LeoLM!
    """)

    context = None
    path_to_upload = None

    option = st.selectbox(
    'Was möchtest du fragen?',
    ('Freie Frage', 'Frage zu einem Dokument'))

    if option == 'Frage zu einem Dokument':
        files = st.file_uploader("File upload", type=["txt", "pdf"], accept_multiple_files=True)

        if len(files) == 0:
            st.info("Keine Datei ausgewählt.")

        if len(files) >= 1:
            for i in range(len(files)):
                path_to_upload = tmpdir_path / files[i].name

                bytes_data = files[i].read() 
                with open(path_to_upload, "wb") as f:
                    f.write(bytes_data) 

                # TODO: Accept multiple files
                break
            
            if len(files) > 1:
                st.warning("Nur eine Datei ist akutell unterstützt! Jede weitere Datei wird ignoriert.")


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
            prompt_history = None
            if len(st.session_state.messages) > 2:
                prompt_history = st.session_state.messages[-2]['promt_history']
                path_to_upload = None
            assistant_response, prompt_history = ask_model(url_server, route_check, route_model, prompt, context, prompt_history, path_to_upload)

            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.1)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response, "promt_history": prompt_history})
