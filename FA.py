import streamlit as st
from streamlit_chat import message
from rag_functions import *

def FA():
    #st.set_page_config(layout='wide')

    if "client" not in st.session_state or "prompt_id" != '522aeebf-7d24-4cf8-995b-087fe410e863':
        st.session_state.URL,st.session_state.headers = init_client()
        st.session_state.prompt_id = '522aeebf-7d24-4cf8-995b-087fe410e863'
        st.session_state.model_name = 'Branch Manager'
        st.session_state.question = 'init'
        st.session_state.answer = 'init'
        st.session_state.source = 'init'
        st.session_state.client = 'init'
        

    st.markdown("<h1 style='text-align: center; color: Black;'>Fleet Assistance Help Desk</h1>", unsafe_allow_html=True)
    st.write("""
    This tool is designed to help answer questions related to Fleet Assistance. To get started ask the tool a question below.

    Example Question: What is the rentalman code to add a reservation?""")


    with st.sidebar:
        feedback_func(
            st.session_state.question,
            st.session_state.answer,
            st.session_state.source,
            st.session_state.prompt_id,
            st.session_state.model_name)

    if 'something' not in st.session_state:
        st.session_state.something = ''

    text = st.text_input("Enter Text Here",key='widget',on_change=submit)

