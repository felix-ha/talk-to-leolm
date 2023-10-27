import streamlit as st
import time


def check_server():
    time.sleep(2)
    return 0


def model(question: str, context: str):
    return question.upper()



st.write("""
# Frag  LeoLM!
""")
   
def check():
    with st.spinner('Wait for it...'):
        status = check_server()
    return status


if st.button('Check Server'):
    if check() == 0:
        st.success('LLM ist online!', icon="✅")
    else: 
        st.warning('LLM ist offline!', icon="⚠️")


