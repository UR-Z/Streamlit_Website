import streamlit as st
from datetime import datetime
import json
import requests
import boto3
import os
from dotenv import load_dotenv
import re
from snowflake.snowpark import Session

load_dotenv('../env.env')

def extract_sources(text):
    # Split the text by newlines
    lines = text.split('\n')
    
    # Filter lines that start with "Source:"
    source_lines = [line for line in lines if line.startswith('Source:')]
    
    # Join the filtered lines back together, preserving newlines
    result = '\n\n'.join(source_lines)
    
    return result


def extract_a_tag_content(text):
    pattern = r'<a.*?>(.*?)</a>'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def snowflake_feedback(prompt_id,model_name,question,answer,source,feedback_choice,additional_feedback):
    connection_parameters = {
    "account": os.getenv('UR_SNOWFLAKE_ACCOUNT'),
    "user": os.getenv('UR_SNOWFLAKE_USERNAME'),
    "password": os.getenv('UR_SNOWFLAKE_PASSWORD'),
    "role": os.getenv('UR_SNOWFLAKE_ROLE'),
    "warehouse": os.getenv('UR_SNOWFLAKE_WAREHOUSE')
    }

    try:
        session = Session.builder.configs(connection_parameters).create()
        st.write('session')
        session.sql("insert into DATALABS.DLA_U_ZCHAN.TENSORINSIGHTS_RAG_FEEDBACK (log_time, prompt_id,model_name,question,answer,source,feedback_choice,additional_feedback ) values (?,?,?,?,?,?,?,?);"
        ,params=[datetime.now(), prompt_id,model_name,question,answer,source,feedback_choice,additional_feedback]).collect()
        st.success('Thank you for your valuable feedback. We will use your feedback to improve the AI model.')
    except Exception as e:
        x= 'bad'
        #st.warning(e)

def snowflake_logging(prompt_id,model_name,question,answer):
    connection_parameters = {
    "account": os.getenv('UR_SNOWFLAKE_ACCOUNT'),
    "user": os.getenv('UR_SNOWFLAKE_USERNAME'),
    "password": os.getenv('UR_SNOWFLAKE_PASSWORD'),
    "role": os.getenv('UR_SNOWFLAKE_ROLE'),
    "warehouse": os.getenv('UR_SNOWFLAKE_WAREHOUSE')
    }

    try:
        session = Session.builder.configs(connection_parameters).create()
        session.sql(
        "insert into DATALABS.DLA_U_ZCHAN.website_logging (log_time, prompt_id,model_name,question,answer ) values (?,?,?,?,?);"
        ,params=[datetime.now(), prompt_id,model_name,question,answer]).collect()
        #print("Connected to Snowflake")
        
    except Exception as e:
        #print("Error connecting to Snowflake")
        #st.write(e)
        x = 'bad'


def submit():
    st.session_state.something = st.session_state.widget
    st.session_state.widget = ''
    st.markdown("<h1 style='text-align: center; color: Black;'>Generated Answer</h1>", unsafe_allow_html=True)
    with st.spinner('Thinking...'):
        st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>You: {st.session_state.something}</div>", unsafe_allow_html=True)
        st.session_state.answer, st.session_state.source = api(st.session_state.prompt_id, st.session_state.something, st.session_state.URL, st.session_state.headers)
        st.session_state.question = st.session_state.something
        st.session_state.col1, st.session_state.col2 = st.columns([3, 3])
        snowflake_logging(st.session_state.prompt_id,st.session_state.model_name,st.session_state.question,st.session_state.answer)
        with st.session_state.col1:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>AI Response: {st.session_state.answer}</div>", unsafe_allow_html=True)

        with st.session_state.col2:
            with st.container(border=True):
                st.markdown(f"""<div style='text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>
                 {extract_sources(st.session_state.source)}</div>""", unsafe_allow_html=True)


        

def init_client():
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
    return URL,headers

def feedback_func(question, answer, source,prompt,model_name):
    with st.container(border=True):
        feedback_options = [
            'Please select an option',
            'Highly accurate document',
            'Accurate document but wrong answer',
            'Inaccurate/no document'
        ]

        feedback_option = st.selectbox(
            label='Please help improve this tool',
            options=feedback_options,
        )
        additional_feedback = st.text_area(
            "Please provide additional feedback (optional)",
        )
        button = st.button('Submit')
        if button and feedback_option != 'Please select an option':
            
            #st.write(f'Logging will be:')
            #st.write(f'RAG Model = ASG Help Desk')
            #st.write(f'Option Selected = {feedback_option}')
            #st.write(f'Additional Feedback = {additional_feedback}')
            #st.write(f'Recorded Date = {datetime.now()}')
            #st.write(f'Question = {question}')
            #st.write(f'Answer = {answer}')
            #st.write(f'Source = {set(extract_a_tag_content(source))}')
            snowflake_feedback(
                prompt_id=prompt,model_name=model_name,question=question,
                answer=answer,source=str(set(extract_a_tag_content(source))),
                feedback_choice=feedback_option,additional_feedback=additional_feedback)
                

                
        elif button and feedback_option == 'Please select an option':
            st.warning('Please select an option from the dropdown.')
def api(prompt_id,question,URL,headers):
    try:
        prompt_id = prompt_id
        body = json.dumps({"search": question,"promptId":prompt_id})
        r = requests.request("POST", URL,data=body,headers=headers)
        response_json = json.loads(r.text)
        x = response_json['result']['answer_text'].split("Sources:")
        return x[0],x[1]
    except:
        st.write('Error, please try again')