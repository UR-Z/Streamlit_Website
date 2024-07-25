import streamlit as st
import os
from dotenv import load_dotenv
import boto3
import json
import requests
import streamlit_scrollable_textbox as stx
load_dotenv('../env.env')

def claude_3(prompt):

    body = json.dumps({
                "max_tokens": 256,
                "messages": [{"role": "user", "content": prompt}],
                "anthropic_version": "bedrock-2023-05-31"
                })

    
        #Run Inference
    modelId = "anthropic.claude-3-haiku-20240307-v1:0"  # change this to use a different version from the model provider if you want to switch 
    accept = "application/json"
    contentType = "application/json"

    bedrock = boto3.client(service_name='bedrock-runtime',region_name='us-west-2',
                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    
    
    return response_body.get('content')[0]['text']


def examples():
    st.markdown("<h1 style='text-align: center; color: Black;'>Everday AI - Use Cases</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: left; color: Black;'>Intro</h1>", unsafe_allow_html=True)
    #st.image('UR_Logo.jpg')
    st.write("""Generative AI represents the next frontier of artificial intelligence, poised to transform how businesses across industries operate. This disruptive technology allows users to generate content like text, images, code, and data insights simply by providing natural language prompts.
            Use the dropdown selector to view example use cases.
            Read the sample ideas and try it yourself!""")
    
    options = ['Email']

    # Create the dropdown selection box
    selected_option = st.selectbox('Select an option', options)

    if selected_option == 'Email':
        col1,col2 = st.columns([3,3])

        with col1:
            st.markdown("<h1 style='text-align: left; color: Black;'>Email Use Case</h1>", unsafe_allow_html=True)
            st.markdown("""Use Gen AI on emails to perform:
- Summarization (take the email and break it down into bullet points)
- Extract Action Items (extract key information from emails)
- Responding to Emails (how do i respond to this email?)
- Assisting with tone (reply to this email with a [positive,negative,funny,etc.] tone)""")
            st.markdown("<h1 style='text-align: left; color: Black;'>Example Email</h1>", unsafe_allow_html=True)
            long_text = """Subject: Weekly Objectives - Operation Hogwarts

Team,

We have an ambitious set of objectives to tackle this week in our ongoing mission. Each one is critical to our success, so I need everyone operating at peak performance. Let's go through them:

Objective Hermione: Our top priority is research and analysis. Just like the brilliant Hermione Granger, we need to immerse ourselves in data, uncover key insights, and develop a comprehensive strategic plan. The future of our endeavors hinges on getting this right.

Objective Ron: Once the analysis is complete, we'll move into execution mode - Ron Weasley style. We need to be scrappy, resourceful, and determined to overcome any obstacles. This phase will test our perseverance and ability to think on our feet.

Objective Harry: The weight of great responsibility rests on our shoulders, not unlike Harry Potter himself. We must demonstrate true leadership - inspiring the team, making tough decisions, and personifying our core values every step of the way. Integrity and moral courage are non-negotiable.

Objective Dumbledore: Wisdom and vision will be indispensable this week. We must keep our eyes on the bigger picture at all times, just as Dumbledore always saw the chessboard several moves ahead. If we lose sight of our long-term goals, we'll be in trouble.

Objective Voldemort: Make no mistake, we have a powerful adversary working against us. Like He-Who-Must-Not-Be-Named, they are cunning, relentless, and will exploit any weaknesses. We must be vigilant and eliminate any vulnerabilities before they can be exposed.

Objective Snape: There will be difficult situations that require courage and sacrifice for the greater good. We may have to make unpopular choices, like Professor Snape, that could put our reputations at risk. Have resolve and know that I will back you up 100%.

Objective McGonagall: Transformation will be key this week. Just as McGonagall could shape-shift into a cat, we too must adapt quickly to changing circumstances. Agility and openness to new approaches will be rewarded.

Objective Weasley Twins: Let's also make sure we keep our sense of humor and look for opportunities to have fun together, no matter how stressful things get. A bit of mischief, like the Weasleys, can go a long way in boosting morale.

I know this is an incredible amount to take on in just 7 days. But I have complete faith that this team has the talents and resolve to make it happen. We are in this fight together against formidable odds. But like the heroes of Hogwarts, our bravery, loyalty, and commitment to each other will see us through.

Stay focused, keep your wands at the ready, and confront each challenge like a true Gryffindor! I'll be providing daily updates and am just an owl away if you need any support.

Let's make some magic happen!"""
            stx.scrollableTextbox(long_text,height = 300)
        with col2:
            st.markdown("<h1 style='text-align: left; color: Black;'>Try it Yourself</h1>", unsafe_allow_html=True)
            if email:=st.chat_input('Enter your input here',key='email'):
                prompt = f"""Respond to the user input defined in the <user input> tag using the email defined in the <email> tag.
<email>
{long_text}
</email>

<user input>
{email}
</user input>
"""
                with st.spinner('Thinking...'):
                    st.write(claude_3(prompt))