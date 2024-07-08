import streamlit as st
import base64
from streamlit_chat import message
from langchain_community.chat_models import BedrockChat
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import pandas as pd
import json

import boto3
import os
from dotenv import load_dotenv
from harsh import *
from help_desk import *
from pca import *
from sales import *



load_dotenv('../env.env')

st.set_page_config(layout='wide')

# Define page functions



def telematics():
    st.markdown("<h1 style='text-align: center; color: Black;'>Service</h1>", unsafe_allow_html=True)
    
def who():
    col1, col2, col3 = st.columns(3)

    with col1:
        # Michel's section
        michel_image = base64.b64encode(open("UR_Logo.jpg", "rb").read()).decode()
        st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{michel_image}" width="400">
            <div style="text-align: center;">
                <strong>Michel</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("Michel's bio goes here...")

    with col2:
        # Zach's section
        zach_image = base64.b64encode(open("UR_Logo.jpg", "rb").read()).decode()
        st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{zach_image}" width="400">
            <div style="text-align: center;">
                <strong>Zach</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("Zach's bio goes here...")

    with col3:
        # Harsh's section
        harsh_image = base64.b64encode(open("UR_Logo.jpg", "rb").read()).decode()
        st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{harsh_image}" width="400">
            <div style="text-align: center;">
                <strong>Harsh</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("Harsh's bio goes here...")

# Function to display the footnote disclosure
def display_footnote():
    st.markdown("""
    <div style='text-align: center; font-size: 12px; color: gray;'>
        The AI system used to generate this content does not collect, store, or process any personally identifiable information (PII). Any PII included in prompts or outputs is incidental and should not be considered a disclosure or transfer of such information. Users are solely responsible for omitting PII from their interactions with the AI. The AI provider makes no representations about the security or privacy of PII in relation to the AI system
    </div>
    """, unsafe_allow_html=True)


# Define the sidebar navigation
navigation = st.sidebar.radio("Select from the following:", ["Main", "Sales","Service","Help Desk","Post Call Analytics"])#, "Telematics", "Who We Are"])


# Display the landing page or the selected page
if navigation == "Main":
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("UR_Logo.jpg", width=200)

    with col2:
        st.subheader("Performance Analytics", anchor=False, divider='blue')
        st.subheader("Gen AI Landing Site", anchor=False)
    #st.markdown("<h1 style='text-align: center; color: Black;'>Performance Analytics - Gen AI </h1>", unsafe_allow_html=True)
    
    # INTRO
    st.write('**Intro**')
    st.write(""" The Performance Analytics department is at the forefront of driving digital innovation within our organization. Our team specializes in leveraging advanced analytics and cutting-edge generative AI technologies to uncover valuable insights and create transformative solutions.

By harnessing the power of data and AI, the Performance Analytics department empowers the organization to make informed, data-driven decisions, helping us stay ahead in an increasingly competitive landscape. Our expertise in advanced analytics allows us to identify patterns, predict trends, and optimize processes, leading to improved efficiency and performance across various business functions.

In addition to our analytics capabilities, we support internal users with their analytic work and tools such as Excel and Tableau. We are happy to provide training to help improve skills and automate tasks, ensuring our team can work more efficiently and effectively.

On the bottom of this page you can try our secure and private LLM running on AWS Bedrock. On the left you can see some demos of current and pasts projects.
""")
    zach = "mailto:zchan@ur.com"
    michel = "mailto:mnahon@ur.com"
    harsh = "mailto:hsurve@ur.com"
    st.write("Feel free to reach out to our team:" " [Harsh Surve](%s),"%harsh,"[Zach Chan](%s)"%zach,"and [Michel Nahon](%s)"%michel )
    # WORK DONE
    st.write('**General Use Tools**')
    st.write('The Performance Analytics department maintains and provides **secure and private** general use AI tools which you can use and access by clicking the image below.')
    # COMMENT/ FEEDBACK

    # SELF SERVICE SECURE GPT
    st.markdown(
        """<a href="http://10.20.129.216:8502/">
        <img src="data:image/png;base64,{}" width="150">
        </a>""".format(
            base64.b64encode(open("click.png", "rb").read()).decode()
        ),
        unsafe_allow_html=True,
    )
    display_footnote()
elif navigation == "Service":
    service()
    display_footnote()
elif navigation == "Sales":
    sales()
    display_footnote()
elif navigation == "Help Desk":
    help_desk()
    display_footnote()
elif navigation == "Post Call Analytics":
    pca()
    display_footnote()
#POC TAB WITH PASSWORD
