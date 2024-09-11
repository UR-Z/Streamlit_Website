import streamlit as st

def service():
    st.markdown("<h1 style='text-align: center; color: Black;'>Service & Maintenance</h1>", unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        #st.write("**UR Manual Assist**")

        url = "http://10.20.129.206:8501/"
        st.write("**UR Manual Assist** - [Demo Tool](%s)" % url)
        st.write("""
            The UR manual assist chatbot is an AI-powered tool that offers answers from equipment service manual, allows users to access specific pages from the PDF and provide feedback.
             
            This tool has been developed with only one goal in mind - MAKE OUR TECH'S LIFE EASY!!!
            
            Key Features - 
            
             1. Chat bot experience for Technicians to get necessary information
             2. LLMs summarize the most relevant information to the question asked as well as provide sources
             3. Ability to view manual pages relevant to the chat bot response
             4. Robust mapping process implemented for each equipment
             
            Gone are the days of waiting in line at the OEM hotline. Simply enter the Equipment Code and the assistant is ready to serve you right away! """)

    with col2:
        st.video('media/UR Manual Assist Demo.mp4')
        st.markdown('**Demo Instructions**')
        st.write("""
                Try it Your Self - 
                
                This tool is meant only for demo purposes. Please ONLY use one of the below equipment. Few sample questions have also been provided.

                Equipment - 11268957 

                Sample questions

                - How to lower platform controls
                - How to disassemble mast 

                Equipment - 3940BLC

                Sample Questions

                - How to assemble main boom 
                - What is roll and leak testing
                """)

             