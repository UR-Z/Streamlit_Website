import streamlit as st

def pca():
    st.markdown("<h1 style='text-align: center; color: Black;'>Post Call Analytics</h1>", unsafe_allow_html=True)
    url = 'https://d2rg3owrlwjuz2.cloudfront.net/'
    st.write("[Demo Tool](%s): username = admin, password = UnitedRentals"%url)
    st.write("""Large language models can be used to analyze phone conversations and other free form text to extract insights.
             Below is an example of Amazon Web Services(AWS) Post Call Analytics tool on field service calls""")
    st.write('**Home screen shows individual processed calls that can be selected for additional information**')
    st.image('pca_call_list.JPG')
    st.write("""**Once a call is selected the user can view baseline details related to duration, time and sentiment**""")
    st.image('call_details_main.JPG')
    st.write("""**The user can also view LLM generated summaries of the call, its relevant context as well as query the call to find additional insights**""")
    st.image('call_details_llm.JPG')
    