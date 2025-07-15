import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("Doctor Assistant")

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_chat" not in st.session_state:
    st.session_state.show_chat = True

main_col, chat_col = st.columns([4, 1.2])

with main_col:
    st.subheader("Patient Information")
    st.markdown("Hier könnten z. B. Labordaten, Symptome etc. stehen.")

if st.session_state.show_chat:
    with chat_col:
        st.markdown("### Assistant (powered by Meditron)")
        chat_container = st.container()

        # Show chat history
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Chat input
        prompt = st.chat_input("Ask something...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Request backend
            try:
                res = requests.post("http://localhost:8000/chat", json={"prompt": prompt})
                data = res.json()
                answer = data["response"]
                state = data["state"]
                num_prompts = data["number_of_prompts"]

            except Exception as e:
                st.error("❌ Backend error: " + str(e))
                st.write("Raw backend response:", res.text)
                answer = f"❌ Backend error: {e}"
                state = "N/A"
                num_prompts = 0

            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(f"{answer}\n\n_State: {state} | History: {num_prompts}_")
            st.session_state.messages.append({"role": "assistant", "content": answer})
