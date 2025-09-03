import streamlit as st
import google.generativeai as genai

st.title("🤖 Gemini Chat")

# API key input
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get and display response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    st.warning("Please enter your Gemini API key in the sidebar")
    st.info("Get your API key from: https://aistudio.google.com/app/apikey")
