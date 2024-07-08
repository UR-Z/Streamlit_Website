import streamlit as st
import os
from dotenv import load_dotenv
import boto3
import json
import requests
load_dotenv('../env.env')

def help_desk():
    client = boto3.client('cognito-idp', region_name = 'us-west-2',
                      aws_access_key_id=os.getenv('TENSOR_AWS_ACCESS_KEY_ID'),aws_secret_access_key=os.getenv('TENSOR_AWS_SECRET_ACCESS_KEY'))
    response = client.initiate_auth(
    #Identity Pool ID
    ClientId="3i4ej8dpcsg0oshtl5k6trpa6f",
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': os.getenv('TENSOR_U'),
        'PASSWORD': os.getenv('TENSOR_P')
    },
)
    access_token = response["AuthenticationResult"]["AccessToken"]
    reponse = client.get_user(AccessToken=access_token)
    URL = "https://8nhdsmf8va.execute-api.us-west-2.amazonaws.com/prod/semantic_search"
    headers = {"Content-Type":"application/json","Authorization":response['AuthenticationResult']['IdToken']}
    st.markdown("<h1 style='text-align: center; color: Black;'>Help Desk</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: left; color: Black;'>Intro</h1>", unsafe_allow_html=True)
    #st.image('UR_Logo.jpg')
    st.write("""RAG is an advanced natural language processing (NLP) technology that combines the power of large language models with external knowledge retrieval capabilities. It allows AI systems to not only generate human-like text based on their training data but also to retrieve and incorporate relevant information from external sources, such as databases, websites, or document repositories.

In a business context, RAG can be a powerful tool for various applications, such as intelligent search and question answering: RAG can be used to build intelligent search engines or virtual assistants that can understand complex queries and provide accurate and relevant answers by retrieving information from multiple sources.
            Use the dropdown selector to view example use cases.""")
    
    options = ['HR', 'IT', 'Telematics']

    # Create the dropdown selection box
    selected_option = st.selectbox('Select an option', options)

    if selected_option == 'HR':
        st.markdown("<h1 style='text-align: left; color: Black;'>HR Help Desk</h1>", unsafe_allow_html=True)
        st.write('Collection of PPBs related to HR')
        st.write('Example Question: what are the biweekly contributions for anthem plan?')
        if hr:=st.chat_input('Here',key='hr'):
            with st.spinner('Thinking...'):
                prompt_id = '673f0900-fbb4-441c-a4f9-861b727feb42'
                body = json.dumps({"search": hr,"promptId":prompt_id})
                r = requests.request("POST", URL,data=body,headers=headers)
                response_json = json.loads(r.text)
                x = response_json['result']['answer_text'].split("Sources:")
                st.write(x[0])
    if selected_option == 'IT':
        st.markdown("<h1 style='text-align: left; color: Black;'>IT Help Desk</h1>", unsafe_allow_html=True)
        st.write('Collection of troubleshooting documentation related to: password, iPad, hardware, printers, software, rentalman and wifi')
        st.write('Example Question: How to reset password?')
        if it:=st.chat_input('Here',key='it'):
            with st.spinner('Thinking...'):
                prompt_id = '91758c11-58c1-4442-8ae1-baf9377f9185'
                body = json.dumps({"search": it,"promptId":prompt_id})
                r = requests.request("POST", URL,data=body,headers=headers)
                response_json = json.loads(r.text)
                x = response_json['result']['answer_text'].split("Sources:")
                st.write(x[0])
    if selected_option == 'Telematics':
        st.markdown("<h1 style='text-align: left; color: Black;'>Telematics Help Desk</h1>", unsafe_allow_html=True)
        st.write('Small collection of documents related to telematics')
        st.write('Example Question: How do i marry a sim and an equipment?')
        if tel:=st.chat_input('Here',key='tel'):
            with st.spinner('Thinking...'):
                prompt_id = '3768e3b8-3310-424b-aafe-04459f3791f5'
                body = json.dumps({"search": tel,"promptId":prompt_id})
                r = requests.request("POST", URL,data=body,headers=headers)
                response_json = json.loads(r.text)
                x = response_json['result']['answer_text'].split("Sources:")
                st.write(x[0])
    
    