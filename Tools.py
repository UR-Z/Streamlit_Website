import streamlit as st
from streamlit_chat import message
from rag_functions import *

def Tools():
    #st.set_page_config(layout='wide')

    if "client" not in st.session_state or "prompt_id" != '1d1888b3-00a0-4a35-8909-da184293e970':
        st.session_state.URL,st.session_state.headers = init_client()
        st.session_state.prompt_id = '1d1888b3-00a0-4a35-8909-da184293e970'
        st.session_state.model_name = 'Tools'
        st.session_state.question = 'init'
        st.session_state.answer = 'init'
        st.session_state.source = 'init'
        st.session_state.client = 'init'
        

    st.markdown("<h1 style='text-align: center; color: Black;'>Tools Help Desk</h1>", unsafe_allow_html=True)
    st.write("""
    This tool is designed to help answer questions related to tools. To get started ask the tool a question below.""")


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

