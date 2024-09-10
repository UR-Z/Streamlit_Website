import streamlit as st
from streamlit_chat import message
import os
from dotenv import load_dotenv
import boto3
import json
import requests
import pandas as pd
from snowflake.snowpark import Session
from datetime import datetime
from streamlit_feedback import streamlit_feedback
import uuid
from asg_functions import *
load_dotenv('../env.env')

def ASG():
    #st.set_page_config(layout='wide')

    if "client" not in st.session_state:
        st.session_state.URL,st.session_state.headers = init_client()
        st.session_state.prompt_id = '3768e3b8-3310-424b-aafe-04459f3791f5'
        st.session_state.question = 'init'
        st.session_state.answer = 'init'
        st.session_state.source = 'init'
        st.session_state.client = 'init'

    st.markdown("<h1 style='text-align: center; color: Black;'>ASG Help Desk</h1>", unsafe_allow_html=True)
    st.write("""
    This tool is designed to help answer questions related to ASG. To get started ask the tool a question below.

    Example Question: How do i marry a telematics device to a piece of equipment?""")


    with st.sidebar:
        feedback_func(st.session_state.question,st.session_state.answer,st.session_state.source)

    if 'something' not in st.session_state:
        st.session_state.something = ''

    text = st.text_input("Enter Text Here",key='widget',on_change=submit)

