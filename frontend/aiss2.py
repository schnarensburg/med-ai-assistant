import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("Doctor Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_chat" not in st.session_state:
    st.session_state.show_chat = True 


# Columns: Left = patient view, Right = assistant
main_col, chat_col = st.columns([4, 1.2])

with main_col:
    st.subheader("Patient Information")
    st.markdown("This is where the medical history, diagnosis, lab reports etc. will go.")

if st.session_state.show_chat:
    with chat_col:
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