import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import os



# Create columns
col1, col2 = st.columns([3,1])

# Place tabs inside the first column
with col1:
    st.markdown("### Patient Act")
    tabs = st.tabs(["Case 1", "Case 2", "Case 3"])

    with tabs[0]:
        # Define columns: 
        col_1, col_2, col_3 = st.columns([1,1,1])
        # Column 1: General information
        with col_1:
            # st.image(os.path.join(os.getcwd(), "static", "Image_Name.jpg"), width = 50)
            st.markdown('''**Patient Number**  
            8''')
            st.markdown('''**Name, Last Name**  
                    Perez, Pepito''')
            st.markdown('''**Sex**  
                     M''')
            st.markdown('''**GP**  
                Dr. Luz Hernandez''')
            st.markdown('''**Height**  
                Dr. Luz Hernandez''')
            st.markdown('''**Weight**  
                Dr. Luz Hernandez''')
            st.markdown('''**Chronic**  
                No''')

        with col_2:
            st.subheader("Diagnosis")
            st.markdown("PERMANENT DIAGNOSIS")

        with col_3:
            st.subheader('Medication')
            st.markdown('PERMANENT MEDICATION')

            # Consultation area
        st.subheader('Prior Consultations')
        
        day, date, type_, text = st.columns([1,1,1,6])
        # Current consultation

        

        # Prior consultations
        
        with day:
            st.markdown('Mo.')

        with date:
            st.write("Right side content")

    with tabs[1]:
        st.line_chart([1, 2, 3])

    with tabs[2]:
        st.text_area("Notes", "Write something...")

# Our Assistant Column
# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_chat" not in st.session_state:
    st.session_state.show_chat = True 

if st.session_state.show_chat:
    with col2:
        st.markdown("### Assistant (powered by Meditron)")
        chat_container = st.container()
        # Show full chat history
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # User input
        prompt = st.chat_input("Ask something...")

        if prompt:
            # Append user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Get response from backend
            with chat_container:
                with st.chat_message("assistant"):
                    msg = st.empty()
                    try:
                        res = requests.post(
                            "http://localhost:8000/chat",
                            json={"prompt": prompt},
                            timeout=10
                        )
                        answer = res.json()["response"]
                    except Exception as e:
                        answer = f"❌ Error contacting backend: {e}"

                    msg.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
    



    ## STREAMLIT CRASH COURSE ##

#min_date = datetime(1974, 3, 11) 
#max_date = datetime.now()
# st.write() --> To write simple things
# st.button("Press me")  (Every time it is pressed the whole script is run and the state changes to "True")

# Text elements
# st.title()
# st.header()
# st.subheader()
# st.markdown ("_Italics_")
# st.caption()
# st.divider()


# images on the screen 
# st.image(os.path.join(os.getcwd(), "static", "Image_Name.jpg"), width = 50)

# Data elements
# st.dataframe(df)
# Data editor section
# editable_df = st.data_editor(df)
# metric section
# st.metric(Label="total rows", value=len(df))

# Form elements
# st.balloons() for balloons in the screen haha


#patient_act = {
#    "name" : None,
#    "height": None,
#    "gender": None,
#    "dob": None
#}

#with st.form(key ="patient_1_ePA"):
#    patient_act["name"] = st.text_input("Patien'ts name")
#    patient_act["height"] = st.number_input("Patient's height (in cm)")
#    patient_act["gender"] = st.selectbox("Sex", ["Male", "Female"])
#    patient_act["dob"] = st.date_input("Birth date:", max_value=max_date, min_value=min_date)


#    submit_button = st.form_submit_button(label="Submit") #Reruns the whole application

#    if submit_button: 
#        if not all(patient_act.values()):
#            st.warning("Please fill in all of the fields")
#        else: 
            
#            st.write("### Info")
           
#Session state: store values within the same user session. E

#if "counter" not in st.session_state:
#    st.session_state.counter = 0 

#if st.button("Increment Counter"):
#    st.session_state.counter += 1
#    st.write(f"Counter incremented to  {st.session_state.counter}")


#Callbacks

#if "step" not in st.session_state:
#    st.session_state.step = 1

#if "info" not in st.session_state: 
#st.session_state = {}

#def go_to_step2(name):
#    st.session_state.info["name"] = name
#    st.session_state.step = 2
 

# Layouts

#Sidebar
#st.sidebar.title("This is the sidebar")
#st.sidebar.write("This is the sidebar content")

#tabs 
#tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
#with tab1: 
#    st.write("Patient 2")

# Container
#with st.container(border=True):
#    st.write("patient")

#st.set_page_config(layout="wide")
#st.title("Doctor Assistant")

#Expander

#Caching: for when connecting to APIs and not rerun everything all the time. So we don't rerun constantly simple operations
 #@st.cache_data this is indefinite cache


## STREAMLIT CRASH COURSE ##




