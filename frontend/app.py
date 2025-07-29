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

# Initialize session state for patient 1
if "consultation_notes" not in st.session_state:
    st.session_state.consultation_notes = []

if "new_note" not in st.session_state:
    st.session_state.new_note = ""

if "reset_note" not in st.session_state:
    st.session_state.reset_note = False

# Data
data_brendas = {
    "Medication": ["Metformin", "Amlodipine", "Promethazine", "Cetirizine", "Tolterodine", "Paracetamol"],
    "Route": ["PO"] * 6,
    "Dose": ["500mg", "5mg", "20mg", "10mg", "2mg", "1g"],
    "Frequency": ["BD", "OD", "OD", "OD", "BD", "QDS"],
    "Duration": ["regular", "regular", "PRN", "regular", "regular", "PRN"]
}

df_brendas = pd.DataFrame(data_brendas)

# Matt Jones

# Initialize session state for patient 2
if "consultation_notes_2" not in st.session_state:
    st.session_state.consultation_notes_2 = []

if "new_note_2" not in st.session_state:
    st.session_state.new_note_2 = ""

if "reset_note_2" not in st.session_state:
    st.session_state.reset_note_2 = False

# Data
data_mattj = {
    "Medication": ["Metformin", "Ramipril", "Bisoprolol", "Dapagliflozin", "Atorvastatin", "Furosemide", "Paracetamol", "Colchine"],
    "Route": ["PO"] * 8,
    "Dose": ["500mg", "10mg", "5mg", "10mg", "20mg", "40mg", "1g", "500 microgram"],
    "Frequency": ["BD", "OD", "OD", "OD", "OD", "BD", "QDS", "BD"],
    "Duration": ["regular", "regular", "regular", "regular", "regular", "regular", "PRN", "regular for 6 days"]
}

df_mattj = pd.DataFrame(data_mattj)


# Jane Smith

# Initialize session state for patient 3
if "consultation_notes_3" not in st.session_state:
    st.session_state.consultation_notes_3 = []

if "new_note_3" not in st.session_state:
    st.session_state.new_note_3 = ""

if "reset_note_3" not in st.session_state:
    st.session_state.reset_note_3 = False

# Data
data_janes = {
    "Medication": [
        "Salbutamol inhaler",
        "Trimbow inhaler (beclometasone dipropionate, formoterol fumarate dihydrate, glycopyrronium bromide)",
        "Azathioprine",
        "Amlodipine",
        "Metformin",
        "Linagliptin",
        "Atorvastatin",
        "Ibuprofen",
        "Naproxen",
        "Paracetamol",
        "Sertraline",
        "Prednisolone"
    ],
    "Route": [
        "Inhalation of aerosol",
        "Inhalation of aerosol",
        "PO",
        "PO",
        "PO",
        "PO",
        "PO",
        "PO",
        "PO",
        "PO",
        "PO",
        "PO"
    ],
    "Dose": [
        "2 puffs",
        "2 puffs",
        "100mg",
        "10mg",
        "1g",
        "5mg",
        "20 mg",
        "400mg",
        "500mg",
        "1g",
        "50mg",
        "Weaning regime (40mg–0mg)"
    ],
    "Frequency": [
        "QDS",
        "BD",
        "Every morning",
        "Every morning",
        "BD",
        "Every morning",
        "Every night",
        "QDS",
        "BD",
        "QDS",
        "Every night",
        "Every morning"
    ],
    "Duration": [
        "PRN",
        "Regular",
        "Regular",
        "Regular",
        "Regular",
        "Regular",
        "Regular",
        "Regular",
        "Regular",
        "Regular",
        "Regular",
        "4 weeks. Reduce by 5mg/5 days. Discharged on Day 2 of 35mg"
    ]
}

df_janes = pd.DataFrame(data_janes)

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
                st.markdown("**Past Medical History:** Diabetes, hypertension, Meniere’s, overactive bladder, hay fever")

            with col03_1:
                st.markdown("**DOB:** 14/03/1958")
                st.markdown("**Weight:** 56Kg")
                st.markdown("**BMI:** 36,8")
                st.markdown("**Chronic:** No")

        with st.container(border=True):
            st.markdown("#### Discharge Letter")

            st.markdown('''**Admitted** 05/06/2025''')
            st.markdown('''**Discharged:** 12/06/2025''')

            st.markdown('''**Clinical treatment summary:**  
            Brenda was brought in by ambulance to hospital with sepsis. Few day history of dysuria, strong smelling dark urine. \
                         Likely source urine, which isolated E. Coli. Treated with gentamicin and recovered rapidly.  
                        Noted to have urge incontinence which patient tells us has been present for a few months now.  
                        Keen to \
                        try a tablet. Investigations and discharge bloods otherwise unremarkable. 
            ''')
            st.markdown('''**Notes for GP:** nil''')
            st.markdown("**Medication changes:** Tolterodine commenced for overactive bladder")
            st.markdown("**Follow-up arrangements:** nil")

        with st.container(border=True):
            st.markdown("#### Medications")
            st.dataframe(df_brendas, use_container_width=True)

        # Horizontal line 
        st.markdown("<hr>", unsafe_allow_html=True)

        # Consultation notes area    
        st.header("Consultation Notes")
        with st.container(border=True):
            st.markdown("#### New Consultation Entry")

            # Use a placeholder key if reset is triggered
            if st.session_state.reset_note:
                st.session_state.reset_note = False
                st.rerun()

            st.text_area("Write your consultation note here...", height=150, key="new_note")

            if st.button("Finish Consultation", key="Finish_consultation_1"):
                if st.session_state.new_note.strip():
                    st.session_state.consultation_notes.append(st.session_state.new_note.strip())
                    st.session_state.reset_note = True  # Trigger rerun without setting new_note directly

        if st.session_state.consultation_notes:
            st.markdown("### Previous Consultations")
            for i, note in enumerate(st.session_state.consultation_notes[::-1], 1):
                with st.container(border=True):
                    st.markdown(f"**Entry #{len(st.session_state.consultation_notes) - i + 1}:**")
                    st.markdown(f"> {note}")  
   
   
    with tabs[1]:
        st.subheader("Patient ID: 99  -  Matt Jones")
        with st.container(border=True):
            col11, col12, col13 = st.columns(3)

            with col11:
                st.image(os.path.join(os.getcwd(), "static", "Jones.png"), width = 200)

            with col12:
                st.markdown("**Age:** 52")
                st.markdown("**Sex:** M")
                st.markdown("**Height:** 162cm")
                st.markdown("**GP:** Dr. Med. M. Acosta")
                st.markdown("**Past Medical History:** Asthma, congestive cardiac failure, CKD 1, hyperthension, diabetes")
            
            with col13:
                st.markdown("**DOB:** 10/01/1973")
                st.markdown("**Weight:** 76Kg")
                st.markdown("**BMI:** 28.95")
                st.markdown("**Chronic:** Yes")

        with st.container(border=True):
            st.markdown("#### Discharge Letter")

            st.markdown('''**Admitted** 05/06/2025''')
            st.markdown('''**Discharged:** 08/06/2025''')

            st.markdown('''**Clinical treatment summary:**  
            Matt a 50 year old presented to A&E with R knee swelling and pain of 5 days duration. 
                        No history of trauma. Joint examination revealed a painful red hot swelling which developed gradually. 
                        Joint aspirated and septic arthritis ruled out with lab analysis.  
                        Crystal microscopy identified negatively birefringent crystals consistent with gout. 
                        Commenced on  colchicine and discharged with colchicine to take home.
            ''')
            st.markdown('''**Notes for GP:** Please note new diagnosis of gout''')
            st.markdown("**Medication changes:** colchicine commenced for gout")
            st.markdown("**Follow-up arrangements:** nil")

        with st.container(border=True):
            st.markdown("#### Medications")
            st.dataframe(df_mattj, use_container_width=True)
  
        # Consultation notes area
        st.header("Consultation Notes")
        with st.container(border=True):
            st.markdown("#### New Consultation Entry")

            if st.session_state.reset_note:
                st.session_state.reset_note = False
                st.rerun()

            st.text_area("Write your consultation note here...", height=150, key="new_note_2")

            if st.button("Finish Consultation", key="Finish_consultation_2"):
                if st.session_state.new_note_2.strip():
                    st.session_state.consultation_notes_2.append(st.session_state.new_note_2.strip())
                    st.session_state.reset_note = True  # Trigger rerun without setting new_note directly

        if st.session_state.consultation_notes_2:
            st.markdown("### Previous Consultations")
            for i, note in enumerate(st.session_state.consultation_notes_2[::-1], 1):
                with st.container(border=True):
                    st.markdown(f"**Entry #{len(st.session_state.consultation_notes_2) - i + 1}:**")
                    st.markdown(f"> {note}")       



    with tabs[2]:
        st.subheader("Patient ID: 15  -  Jane Smith")
        with st.container(border=True):
            col21, col22, col23 = st.columns(3)

            with col21:
                st.image(os.path.join(os.getcwd(), "static", "Jones.png"), width = 200)

            with col22:
                st.markdown("**Age:** 68")
                st.markdown("**Sex:** F")
                st.markdown("**Height:** 167cm")
                st.markdown("**GP:** Dr. Med. M. Ruiz")
                st.markdown("**Past Medical History:** COPD, ILD, OA knee, hypertension, depression, new T2DM")
            
            with col23:
                st.markdown("**DOB:** 10/01/1955")
                st.markdown("**Weight:** 105Kg")
                st.markdown("**BMI:** 28.95")
                st.markdown("**Chronic:** Yes")

        with st.container(border=True):
            st.markdown("#### Discharge Letter")

            st.markdown('''**Admitted** 05/06/2025''')
            st.markdown('''**Discharged:** 12/06/2025''')

            st.markdown('''**Clinical treatment summary:**  
            Jane a 68-year-old female was brought in by ambulance for shortness of breath. 
            She is a known recurrent attender for COPD exacerbations, last attendance 9 weeks prior.  
            Presented after rescue pack failed to resolve symptoms after 3 days use. Desaturations at home to 84%
            breathing room air. Chest X-ray demonstrated chronic fibrotic changes with overlying right lower zone consolidation.
            Producing green sputum with a severe cough responsive to nebulisers, chest physiotherapy and escalated antibiotic 
            and steroid treatment.  
            Discovered to have raised BMs on this admission and diagnosed with T2DM.  
            Jane is not a candidate for LTOT, due to being a current smoker.
            ''')
            st.markdown('''**Notes for GP:** Please note new diagnosis T2DM''')
            st.markdown("**Medication changes:**  weaning steroid regime, commenced on metformin and linagliptin")
            st.markdown('''**Follow-up arrangements:**  Follow up CXR in 6 weeks time.  
            DSN review 2-4 weeks post discharge in community ''')

        with st.container(border=True):
            st.markdown("#### Medications")
            st.dataframe(df_mattj, use_container_width=True)
  
        # Consultation notes area
        st.header("Consultation Notes")
        with st.container(border=True):
            st.markdown("#### New Consultation Entry")

            if st.session_state.reset_note:
                st.session_state.reset_note = False
                st.rerun()

            st.text_area("Write your consultation note here...", height=150, key="new_note_2")

            if st.button("Finish Consultation", key="Finish_consultation_2"):
                if st.session_state.new_note_2.strip():
                    st.session_state.consultation_notes_2.append(st.session_state.new_note_2.strip())
                    st.session_state.reset_note = True  # Trigger rerun without setting new_note directly

        if st.session_state.consultation_notes_2:
            st.markdown("### Previous Consultations")
            for i, note in enumerate(st.session_state.consultation_notes_2[::-1], 1):
                with st.container(border=True):
                    st.markdown(f"**Entry #{len(st.session_state.consultation_notes_2) - i + 1}:**")
                    st.markdown(f"> {note}")       




# --- Backend Communication ---
def ask_ai(user_prompt):
    url = "http://127.0.0.1:8000/chat"
    payload = {"prompt": user_prompt, "user_id": "user_1"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "No answer returned.")
    except requests.exceptions.RequestException as e:
        return f"Error contacting backend: {e}"

def assistant_ui():
    # Session State Init
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "show_chat" not in st.session_state:
        st.session_state.show_chat = True

    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = ""

    with col2:
        # STEP 1: Handle input FIRST
        user_prompt = st.session_state.get("pending_prompt")
        if user_prompt and user_prompt != st.session_state.last_prompt:
            st.session_state.last_prompt = user_prompt
            st.session_state.messages.append({"role": "user", "content": user_prompt})

            response = ask_ai(user_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Clear pending input after processing
            st.session_state.pending_prompt = ""
            st.rerun()

        # STEP 2: Display Chat
        if st.session_state.show_chat:
            st.markdown("### Assistant (powered by Meditron)")

            st.markdown("""
                <style>
                    .chat-box {
                        height: 500px;
                        overflow-y: auto;
                        padding: 1rem;
                        border: 1px solid #ddd;
                        background-color: #f9f9f9;
                        border-radius: 10px;
                        margin-bottom: 1rem;
                    }
                    .user-msg {
                        background-color: #DCF8C6;
                        padding: 10px 15px;
                        border-radius: 10px;
                        margin: 5px 0;
                        text-align: right;
                        color: black;
                    }
                    .assistant-msg {
                        background-color: #e5e5ea;
                        padding: 10px 15px;
                        border-radius: 10px;
                        margin: 5px 0;
                        text-align: left;
                        color: black;
                    }
                </style>
                <script>
                    function scrollChatToBottom(){
                        const chatDiv = window.parent.document.getElementById("chat-box");
                        if(chatDiv){
                            chatDiv.scrollTop = chatDiv.scrollHeight;
                        }
                    }
                    window.addEventListener("load", scrollChatToBottom);
                    setTimeout(scrollChatToBottom, 100);
                </script>
            """, unsafe_allow_html=True)

            with st.container():
                chat_html = '<div class="chat-box" id="chat-box">'
                for msg in st.session_state.messages:
                    role = msg["role"]
                    content = msg["content"]
                    css_class = "user-msg" if role == "user" else "assistant-msg"
                    chat_html += f'<div class="{css_class}">{content}</div>'
                chat_html += '</div>'
                st.markdown(chat_html, unsafe_allow_html=True)

        # STEP 3: Show chat input at bottom, logic is decoupled
        new_prompt = st.chat_input("Ask something...")
        if new_prompt:
            st.session_state.pending_prompt = new_prompt
            st.rerun()

# --- Run App ---
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
 