import streamlit as st
from streamlit_chat import message
from rag_functions import *

def IT():
    #st.set_page_config(layout='wide')

    if "client" not in st.session_state or "prompt_id" != '91758c11-58c1-4442-8ae1-baf9377f9185':
        st.session_state.URL,st.session_state.headers = init_client()
        st.session_state.prompt_id = '91758c11-58c1-4442-8ae1-baf9377f9185'
        st.session_state.model_name = 'IT Help'
        st.session_state.question = 'init'
        st.session_state.answer = 'init'
        st.session_state.source = 'init'
        st.session_state.client = 'init'
        

    st.markdown("<h1 style='text-align: center; color: Black;'>IT Help Desk</h1>", unsafe_allow_html=True)
    st.write("""
    This tool is designed to help answer questions related to IT. To get started ask the tool a question below.

    Example Question: How do i connect to a zebra printer?""")


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

