import os
import time
import requests
import json
import streamlit as st


ip_adress_server = os.getenv('IP_ADRESS_SERVER', 'localhost')
port = 5000
url_server = f'http://{ip_adress_server}:{port}'
route_check = '/up-status'
route_mock_model = '/mock-llm'
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
    
def ask_model(url_server: str, route_model: str, question: str, context: str):
    payload = {'question': question, 'context': context}
    headers = {'content-type': 'application/json'}
    response = requests.post(f'{url_server}/{route_model}', data=json.dumps(payload), headers=headers)
    return response.json()

def mock_ask_model(question: str, context: str):
    time.sleep(1)
    return{'inference_time_seconds': 1.5181848, 'answer': "Das weiß ich nicht."}



st.write("""
# Frag  LeoLM!
""")
   
if st.button('Check Server'):
    with st.spinner('Wait for it...'):
        if server_is_online(url_server, route_check):
            st.success('LLM ist online!', icon="✅")
        else:
            st.warning('LLM ist offline!', icon="⚠️")


# Input --------------------------------


# Context -----------------------------

# option = st.selectbox(
#     'Zu welchem Inhalt möchtest du eine Frage stellen?',
#     ('Kein Kontext', 'Freitext'))

context = None

# if option == 'Freitext':
#     context = st.text_area(
#     "Kontext",
#     "",
#     )

# Question -------------------------------------------

question = st.text_area(
    "Frage",
    "",
    )

if st.button('Stelle Frage'):
    if server_is_online(url_server, route_check):
      if question != "":
          with st.spinner('LLM denkt...'):
              result = ask_model(url_server, route_mock_model, question, context)
              st.text_area(f'Antwort (dauerte {result["inference_time_seconds"]:.2f} Sekunden)', result['answer'])
    else:
      st.warning('LLM ist offline, keine Antwort möglich!', icon="⚠️")