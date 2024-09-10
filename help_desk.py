import streamlit as st
import os
from dotenv import load_dotenv
import boto3
import json
import requests
from snowflake.snowpark import Session
from datetime import datetime
from streamlit_feedback import streamlit_feedback
import uuid

# Disable warnings
#st.set_option('deprecation.showfileUploaderEncoding', False)
#st.set_option('deprecation.showPyplotGlobalUse', False)

load_dotenv('../env.env')

if 'fbk' not in st.session_state:
    st.session_state.fbk = str(uuid.uuid4())

    st.session_state.question = None

    st.session_state.answer = None

def fb(question,answer,prompt_id,model_name):
      #FEEDBACK
        with st.container(border=True):
            st.write('Feedback:')
            #st.write(uuid.uuid4())

            streamlit_feedback(
                feedback_type="thumbs",
                optional_text_label="[Optional] Please provide an explanation",
                align="flex-start",
                key=st.session_state.fbk)

            fb = st.session_state[st.session_state.fbk]
            if fb:
                #data_to_store = [(message) for message in st.session_state.messages]
                #st.write(question,answer)
                
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {question}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {answer}</div>", unsafe_allow_html=True)
                st.write(str(fb))

                snowflake_feedback(log_time=datetime.now(), prompt_id=prompt_id,model_name=model_name,question=question,answer=answer,feedback=str(fb))

                st.success(f'Thank you for your valuable feedback. We will use your feedback to improve the AI model.')

def snowflake_feedback(log_time, prompt_id,model_name,question,answer,feedback):
    connection_parameters = {
    "account": os.getenv('SNOWFLAKE_ACCOUNT'),
    "user": os.getenv('SNOWFLAKE_USERNAME'),
    "password": os.getenv('SNOWFLAKE_PASSWORD'),
    "role": "ANALYST",
    "warehouse": "WH_ADHOC",
    "database": "DISCOVERY",
    "schema": "DLA_U_ZCHAN"
    }

    try:
        session = Session.builder.configs(connection_parameters).create()
        session.sql(
        "insert into discovery.DLA_U_ZCHAN.website_feedback (log_time, prompt_id,model_name,question,answer,feedback ) values (?,?,?,?,?,?);"
        ,params=[log_time, prompt_id,model_name,question,answer,feedback]).collect()
        #print("Connected to Snowflake")
    except Exception as e:
        #print("Error connecting to Snowflake")
        #st.write(e)
        x= 'bad'

def snowflake_logging(log_time, prompt_id,model_name,question,answer):
    connection_parameters = {
    "account": os.getenv('SNOWFLAKE_ACCOUNT'),
    "user": os.getenv('SNOWFLAKE_USERNAME'),
    "password": os.getenv('SNOWFLAKE_PASSWORD'),
    "role": "ANALYST",
    "warehouse": "WH_ADHOC",
    "database": "DISCOVERY",
    "schema": "DLA_U_ZCHAN"
    }

    try:
        session = Session.builder.configs(connection_parameters).create()
        session.sql(
        "insert into discovery.DLA_U_ZCHAN.website_logging (log_time, prompt_id,model_name,question,answer ) values (?,?,?,?,?);"
        ,params=[log_time, prompt_id,model_name,question,answer]).collect()
        #print("Connected to Snowflake")
    except Exception as e:
        #print("Error connecting to Snowflake")
        #st.write(e)
        x= 'bad'

def feedback(model, question, answer):
    with st.container(border=True):
        feedback_options = [
            'Please select an option',
            'Highly reliable and accurate document retrieval (Green)',
            'Generally reliable with minor inaccuracies (Yellow)',
            'Somewhat unreliable with moderate inaccuracies (Orange)',
            'Unreliable and inaccurate document retrieval (Red)'
        ]

        feedback_option = st.selectbox(
            label='Please help improve this tool',
            options=feedback_options,
        )
        additional_feedback = st.text_area(
                "Please provide additional feedback (optional)",
            )
        button = st.button('Submit')
        if button:
            
            st.success(f'Thank you for your valuable feedback. We will use your feedback to improve the AI model.')
            st.write(f'Logging will be:')
            st.write(f'RAG Model = {model}')
            st.write(f'Option Selected = {feedback_option}')
            st.write(f'Additional Feedback = {additional_feedback}')
            st.write(f'Recorded Date = {datetime.now()}')

def api(prompt_id,question,URL,headers):
    try:
        prompt_id = prompt_id
        body = json.dumps({"search": question,"promptId":prompt_id})
        r = requests.request("POST", URL,data=body,headers=headers)
        response_json = json.loads(r.text)
        x = response_json['result']['answer_text'].split("Sources:")
        return x[0]
    except:
        st.write('Error, please try again')
            
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
    
    options = ['HR', 'IT', 'Telematics','Fleet Assistance','PPB','RFP']

    # Create the dropdown selection box
    selected_option = st.selectbox('Select an option', options)

    if selected_option == 'HR':
        st.markdown("<h1 style='text-align: left; color: Black;'>HR Help Desk</h1>", unsafe_allow_html=True)
        st.write('Collection of PPBs related to HR')
        st.write('Example Question: what are the biweekly contributions for anthem plan?')
        prompt_id = '673f0900-fbb4-441c-a4f9-861b727feb42'
        if hr:=st.chat_input('Enter your question here',key='hr'):
            st.session_state.question = hr
            with st.spinner('Thinking...'):
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {hr}</div>", unsafe_allow_html=True)
                x = api(prompt_id,hr,URL,headers)
                st.session_state.answer = x
                snowflake_logging(log_time=datetime.now(), prompt_id=prompt_id,model_name='HR Help Desk',question=hr,answer=x)
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {x}</div>", unsafe_allow_html=True)
    #if st.session_state.question is not None:
    #    fb(st.session_state.question, st.session_state.answer,prompt_id,'HR Help Desk')

    if selected_option == 'IT':
        st.markdown("<h1 style='text-align: left; color: Black;'>IT Help Desk</h1>", unsafe_allow_html=True)
        st.write('Collection of troubleshooting documentation related to: password, iPad, hardware, printers, software, rentalman and wifi')
        st.write('Example Question: How to reset password?')
        prompt_id = '91758c11-58c1-4442-8ae1-baf9377f9185'
        if it:=st.chat_input('Enter your question here',key='it'):
            st.session_state.question = it
            with st.spinner('Thinking...'):
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {it}</div>", unsafe_allow_html=True)
                x = api(prompt_id,it,URL,headers)
                st.session_state.answer = x
                snowflake_logging(log_time=datetime.now(), prompt_id=prompt_id,model_name='IT Help Desk',question=it,answer=x)
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {x}</div>", unsafe_allow_html=True)
    #if st.session_state.question is not None:
    #    fb(st.session_state.question, st.session_state.answer, prompt_id, 'IT Help Desk')
    if selected_option == 'Telematics':
        st.markdown("<h1 style='text-align: left; color: Black;'>Telematics Help Desk</h1>", unsafe_allow_html=True)
        st.write('Small collection of documents related to telematics')
        st.write('Example Question: How do i marry a sim and an equipment?')
        prompt_id = '3768e3b8-3310-424b-aafe-04459f3791f5'
        if tel:=st.chat_input('Enter your question here',key='tel'):
            st.session_state.question = tel
            with st.spinner('Thinking...'):
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {tel}</div>", unsafe_allow_html=True)
                x = api(prompt_id,tel,URL,headers)
                st.session_state.answer = x
                snowflake_logging(log_time=datetime.now(), prompt_id=prompt_id,model_name='Telematics Help Desk',question=tel,answer=x)
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {x}</div>", unsafe_allow_html=True)
    #if st.session_state.question is not None:    
    #    fb(st.session_state.question, st.session_state.answer, prompt_id, 'Telematics Help Desk')
    if selected_option == 'Fleet Assistance':
        st.markdown("<h1 style='text-align: left; color: Black;'>Fleet Assistance</h1>", unsafe_allow_html=True)
        st.write('Small collection of documents related information that would help branch managers')
        st.write('Example Question: What is the rentalman code to add a reservation?')
        prompt_id = '522aeebf-7d24-4cf8-995b-087fe410e863'
        if fleet:=st.chat_input('Enter your question here',key='fleet'):
            st.session_state.question = fleet
            with st.spinner('Thinking...'):
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {fleet}</div>", unsafe_allow_html=True)
                x = api(prompt_id,fleet,URL,headers)
                st.session_state.answer = x
                snowflake_logging(log_time=datetime.now(), prompt_id=prompt_id,model_name='Fleet Assistance',question=fleet,answer=x)
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {x}</div>", unsafe_allow_html=True)
    #if st.session_state.question is not None:
    #    fb(st.session_state.question, st.session_state.answer, prompt_id, 'Fleet Assistance')
    if selected_option == 'RFP':
        st.markdown("<h1 style='text-align: left; color: Black;'>RFP Help Desk</h1>", unsafe_allow_html=True)
        st.write('Small collection of documents related to RFP')
        st.write('Example Question: What is a WEDGE system?')
        prompt_id = '6b83fd17-a7a4-40bf-923f-8e43ea3bf1b7'
        if rfp:=st.chat_input('Enter your question here',key='rfp'):
            st.session_state.question = rfp
            with st.spinner('Thinking...'):
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {rfp}</div>", unsafe_allow_html=True)
                x = api(prompt_id,rfp,URL,headers)
                st.session_state.answer = x
                snowflake_logging(log_time=datetime.now(), prompt_id=prompt_id,model_name='RFP Help Desk',question=rfp,answer=x)
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {x}</div>", unsafe_allow_html=True)
    #if st.session_state.question is not None:
    #    fb(st.session_state.question, st.session_state.answer, prompt_id, 'RFP Help Desk')
    if selected_option == 'PPB':
        st.markdown("<h1 style='text-align: left; color: Black;'>PPB Help Desk</h1>", unsafe_allow_html=True)
        st.write('Small collection of documents related to PPB')
        st.write('Example Question: What is the current vacation policy?')
        prompt_id = '0d69c036-e10f-40c5-95cc-356a7f405e50'
        if ppb:=st.chat_input('Enter your question here',key='ppb'):
            st.session_state.question = ppb
            with st.spinner('Thinking...'):
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {ppb}</div>", unsafe_allow_html=True)
                x = api(prompt_id,ppb,URL,headers)
                st.session_state.answer = x
                snowflake_logging(log_time=datetime.now(), prompt_id=prompt_id,model_name='PPB Help Desk',question=ppb,answer=x)
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {x}</div>", unsafe_allow_html=True)
    #if st.session_state.question is not None:
    #    fb(st.session_state.question, st.session_state.answer, prompt_id, 'PPB Help Desk')
    
    