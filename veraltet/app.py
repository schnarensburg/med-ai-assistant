import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("Doctor Assistant")

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_chat" not in st.session_state:
    st.session_state.show_chat = True

main_col, chat_col = st.columns([2.5, 3])

with main_col:
    st.subheader("Patient Information")

    # Basisdaten
    with st.expander("🧑‍⚕️ Basic Data"):
        st.text_input("Name")
        st.number_input("Age", min_value=0, max_value=120, step=1)
        st.selectbox("Gender", ["", "Male", "Female", "Other"])

    # Symptombeschreibung
    with st.expander("🩻 Symptoms"):
        st.text_area("Describing Symptoms")
        st.text_input("Diagnosis (if known)")
        st.date_input("Date")

    # Labordaten und Datei-Upload
    with st.expander("📄 Uploads"):
        uploaded_file = st.file_uploader("Upload PDF, TXT, CSV...", type=["pdf", "txt", "csv"])
        if uploaded_file:
            st.success(f"✅ received file: {uploaded_file.name}")
            # TODO: Weiterleitung ans Backend

if st.session_state.show_chat:
    with chat_col:
        st.markdown("### Assistant (powered by Meditron)")
        chat_container = st.container()

        # Show chat history
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        prompt = st.chat_input("Ask something...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Request backend
            try:
                with st.spinner("🧠 Processing..."):
                    res = requests.post(
                        "http://localhost:8000/chat",
                        json={"prompt": prompt, "user_id": "user_1"},
                        timeout=30
                    )
                    data = res.json()
                    answer = data["response"]
                    state = data["state"]
                    num_prompts = data["number_of_prompts"]

            except requests.exceptions.RequestException as e:
                st.error("❌ Backend error: " + str(e))
                answer = f"❌ Backend error: {e}"
                state = "N/A"
                num_prompts = 0

            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(f"{answer}\n\n_State: {state} | History: {num_prompts}_")

            st.session_state.messages.append({"role": "assistant", "content": answer})
