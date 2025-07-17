import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import os

st.set_page_config(
    page_title="Patient Dashboard",
    layout="wide",         
    initial_sidebar_state="collapsed"
)

# Patient Data 

# Brenda Smith

data = {
    "Medication": ["Metformin", "Amlodipine", "Promethazine", "Cetirizine", "Tolterodine", "Paracetamol"],
    "Route": ["PO"] * 6,
    "Dose": ["500mg", "5mg", "20mg", "10mg", "2mg", "1g"],
    "Frequency": ["BD", "OD", "OD", "OD", "BD", "QDS"],
    "Duration": ["regular", "regular", "PRN", "Regular", "Regular", "PRN"]
}

df = pd.DataFrame(data)



# Create columns
col1, col2 = st.columns([2,1])

# Place tabs inside the first column
with col1:
    st.header("Patient Act")
    tabs = st.tabs(["Case 1", "Case 2", "Case 3"])

    with tabs[0]:
        st.subheader("Patient ID: 8  -  Brenda Smith")
        with st.container(border=True):
            col01_1, col02_1, col03_1 = st.columns(3)

            with col01_1:
                st.image(os.path.join(os.getcwd(), "static", "Smith.png"), width = 180)

            with col02_1:
                st.markdown("**Age:** 67")
                st.markdown("**Sex:** Female")
                st.markdown("**Height:** 152cm")
                st.markdown("**GP:** Dr. Med. M. Müller")

            with col03_1:
                st.markdown("**DOB:** 14/03/1947")
                st.markdown("**Weight:** 56Kg")
                st.markdown("**BMI:** 36,8")
                st.markdown("**Chronic:** No")

        with st.container(border=True):
            st.markdown("#### Discharge Letter")

            st.markdown('''**Clinical treatment summary:**  
            Brenda was brought in by ambulance to hospital with sepsis. Few day history of dysuria, strong smelling dark urine. \
                         Likely source urine, which isolated E. Coli. Treated with gentamicin and recovered rapidly.  
                        Noted to have urge incontinence which patient tells us has been present for a few months now.  
                        Keen to \
                        try a tablet. Invstigations and discharge bloods otherwise unremarkable. 
            ''')
            st.markdown('''**Notes for GP:** nil''')
            st.markdown("**Medication changes:** Tolterodine commenced for overactive bladder")
            st.markdown("**Follow-up arrangements:** nil")

        with st.container(border=True):
            st.markdown("#### Medications")
            st.dataframe(df, use_container_width=True)


        # Horizontal line (optional)
        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("More detailed sections below...")

    with tabs[1]:
        with st.container(border=True):
            col11, col12, col13 = st.columns(3)

            with col11:
                st.image(os.path.join(os.getcwd(), "static", "Smith.png"), width = 200)

            with col12:
                st.markdown("**Patient ID:** 9")
                st.markdown("**Sex:** F")
                st.markdown("**Age:** 68")
                st.markdown("**Height:** 167cm")

            with col13:
                st.markdown("**Name:** Jane Eyre")
                st.markdown("**DOB:** 20/01/1955")
                st.markdown("**Weight:** 105Kg")
                st.markdown("**Chronic:** Yes")

        # Horizontal line (optional)
        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("More detailed sections below...")

    with tabs[2]:
        st.text_area("Notes", "Write something...")

# --- Assistant Functionality with Backend Integration ---

def ask_ai(user_prompt):
    url = "http://127.0.0.1:8000/chat"
    payload = {"prompt": user_prompt, "user_id": "user_1"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "⚠️ No answer returned.")
    except requests.exceptions.RequestException as e:
        return f"Error contacting backend: {e}"

def assistant_ui():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "show_chat" not in st.session_state:
        st.session_state.show_chat = True 

    if st.session_state.show_chat:
        with col2:
            st.markdown("### Assistant (powered by Meditron)")
            chat_container = st.container()

            # Display chat history
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            

            # User input
            prompt = st.chat_input("Ask something...")

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        msg = st.empty()
                        answer = ask_ai(prompt)
                        msg.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})

# --- Call the Assistant UI ---
assistant_ui()


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


# Isolate effects: being on the quadrnt gives little information. The message should be more important and it could be actionable. 

# Message + matrix + steering are 3 effects, but we cannot isolate them 

# Having a figure of how we evaluated the system and how we evaluated the effects
# Make it really formal. Confidence, cognitive load, intention to use later 
# Overview of the study and variables that we want to ask to the participants. 
# WHat factors are interesting? How many messages do they need to come out with the correct conclusion? 
# How likely are they to come up with a solution? 

## STREAMLIT CRASH COURSE ##
 