import streamlit as st
def sales():
    st.markdown("<h1 style='text-align: center; color: Black;'>Sales</h1>", unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1:
        st.write("**Project Overview: Speak the Order – OSR Form Filler**")
        url = "https://voiceorder.ur.com"
        st.write("[**Demo**]](%s)" % url)
        st.write("""
Idea:
- Develop an AI-driven system to converse between outside sales representatives (OSR) to enable quicker access to internal data
- Collect information needed for a reservation as the employee converses naturally with a bot
- Ability to create a draft order into an employee's UR Max account

Technologies:
- Natural Language Processing (NLP): Utilize NLP techniques to process and understand unstructured text data from employee interactions
- Generative AI (Gen AI): Employ state-of-the-art large language models (LLMs) to generate human-like responses and content based on employee inputs
- Cloud Computing: Leverage elastic compute systems to deploy the tool for users to access
""")
    
        
    with col2:
        st.video('speak_the_order.mp4')