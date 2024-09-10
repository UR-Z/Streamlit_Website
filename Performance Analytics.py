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
from examples import *
from asg_help_desk import *
from ASG import ASG
from HR import HR

#st.set_option('deprecation.showfileUploaderEncoding', False)
#st.set_option('deprecation.showPyplotGlobalUse', False)



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
navigation = st.sidebar.radio("Select from the following:",
["Main", "ASG", "1HR", "Everyday AI","Sales","Service","Post Call Analytics","ASG/Telematics Help Desk","Help Desk"])#, "Telematics", "Who We Are"])

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
    st.write("""This site has been built to show some of the capabilities of Gen AI. 

On the left side you can select tabs with examples and opportunities to try the tools yourself.

You can find examples related to: 
<ul>
    <li>Telematics</li>
    <li>Sales</li>
    <li>Service</li>
    <li>IT</li>
    <li>HR</li>
</ul>

""",unsafe_allow_html=True)
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
elif navigation == "ASG":
    ASG()
    display_footnote()
elif navigation == "1HR":
    HR()
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
elif navigation == "Everyday AI":
    examples()
    display_footnote()
elif navigation == "ASG/Telematics Help Desk":
    asg_help_desk()
    display_footnote()
#POC TAB WITH PASSWORD
