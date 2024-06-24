import streamlit as st
import boto3
from streamlit_chat import message
from langchain_community.chat_models import BedrockChat
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import os
from dotenv import load_dotenv
import pandas as pd
import json
load_dotenv('../env.env')

def claude_3(prompt):

    body = json.dumps({
                "max_tokens": 200000,
                "messages": [{"role": "user", "content": prompt}],
                "anthropic_version": "bedrock-2023-05-31"
                })

    
        #Run Inference
    modelId = "anthropic.claude-3-opus-20240229-v1:0"  # change this to use a different version from the model provider if you want to switch 
    accept = "application/json"
    contentType = "application/json"

    bedrock = boto3.client(service_name='bedrock-runtime',region_name='us-west-2',
                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    
    
    return response_body.get('content')[0]['text']

def self_serve():
    # Set the theme to dark mode
    st.markdown(
        """
        <style>
        body {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Define the sidebar
    with st.sidebar:
        option = st.selectbox("Choose an option", ["UR-GPT", "Document Summarization"])

    # Display the corresponding output
    if option == "UR-GPT":
        bedrock = boto3.client(service_name='bedrock-runtime',region_name='us-west-2',aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        model_sel = "anthropic.claude-v2"
        chat = BedrockChat(model_id=model_sel,client = bedrock )
        # initialize message history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                SystemMessage(content="You are a helpful assistant.")
            ]

        st.header("UR Secure ChatGPT 🤖")
        #Auto clear text input
        if 'something' not in st.session_state:
            st.session_state.something = ''

        # sidebar with user input
        #with st.sidebar:
        user_input = st.text_input("Your Input: ", key="widget",on_change=submit)

        # handle user input
        if  st.session_state.something != '':
            st.session_state.messages.append(HumanMessage(content=st.session_state.something))
            with st.spinner("Thinking..."):
                response = chat(st.session_state.messages)
            st.session_state.messages.append(
                AIMessage(content=response.content))

        # display message history
        messages = st.session_state.get('messages', [])
        for i, msg in enumerate(messages[1:]):
            if i % 2 == 0:
                message(msg.content, is_user=True, key=str(i) + '_user')
            else:
                message(msg.content, is_user=False, key=str(i) + '_ai')
    elif option == "Document GPT":
        input_csv = st.file_uploader("Upload your CSV file", type=['csv'])

        if input_csv is not None:

            col1, col2 = st.columns([1,1])

            with col1:
                st.info("CSV Uploaded Successfully")
                data = pd.read_csv(input_csv)
                st.dataframe(data, use_container_width=True)

            with col2:

                st.info("Chat Below")
                
                input_text = st.text_area("Enter your query")

                if input_text is not None:
                    if st.button("Chat with CSV"):
                        st.info("Your Query: "+input_text)
                        query = f"""Given the following data in the <data> tag, answer the question in the <query> tag.
<data>
{data}
</data>

<query>
{input_text}
</query>
"""


                        result = claude_3(query)
                        st.success(result)
