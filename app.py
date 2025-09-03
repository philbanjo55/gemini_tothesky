import streamlit as st
import google.generativeai as genai
from PIL import Image
import tempfile
import os

st.title("烙 Gemini Chat with Video & Image Support")

# API key input
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.write(message["content"])
            elif message["type"] == "image":
                st.image(message["content"], caption="Uploaded Image")
            elif message["type"] == "video":
                st.video(message["content"])
    
    # File upload section
    st.sidebar.markdown("###  Upload Files")
    uploaded_files = st.sidebar.file_uploader(
        "Choose images or videos", 
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'mp4', 'mov', 'avi', 'wmv'],
        accept_multiple_files=True
    )
    
    # Chat input
    if prompt := st.chat_input("Ask about text, images, or videos..."):
        
        # Prepare content for API
        content_parts = [prompt]  # Start with text prompt
        
        # Process uploaded files
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_type = uploaded_file.type
                
                if file_type.startswith('image/'):
                    # Handle image files
                    image = Image.open(uploaded_file)
                    content_parts.append(image)
                    
                    # Add to chat history for display
                    st.session_state.messages.append({
                        "role": "user", 
                        "type": "image", 
                        "content": image
                    })
                    
                elif file_type.startswith('video/'):
                    # Handle video files
                    # Save video temporarily for processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name
                    
                    # Upload video to Gemini and wait for processing
                    st.info(f"⏳ Uploading and processing video: {uploaded_file.name}")
                    video_file = genai.upload_file(tmp_path)
                    
                    # Wait for video to be processed
                    import time
                    while video_file.state.name == "PROCESSING":
                        st.info(" Video is still processing, please wait...")
                        time.sleep(2)
                        video_file = genai.get_file(video_file.name)
                    
                    if video_file.state.name == "FAILED":
                        st.error("❌ Video processing failed. Please try a different video.")
                        os.unlink(tmp_path)
                        continue
                    
                    st.success("✅ Video processed successfully!")
                    content_parts.append(video_file)
                    
                    # Add to chat history for display
                    st.session_state.messages.append({
                        "role": "user", 
                        "type": "video", 
                        "content": uploaded_file
                    })
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
        
        # Add user text message to history
        st.session_state.messages.append({
            "role": "user", 
            "type": "text", 
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            if uploaded_files:
                st.write(f" {len(uploaded_files)} file(s) attached")
        
        # Get and display Gemini response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing content..."):
                try:
                    response = model.generate_content(content_parts)
                    st.write(response.text)
                    
                    # Add assistant response to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "type": "text", 
                        "content": response.text
                    })
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Make sure your files are supported formats and try again.")
    
    # Clear chat button
    if st.sidebar.button("️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

else:
    st.warning("⚠️ API key is hardcoded - anyone can use this app and consume your quota!")
    st.info("For production use, consider using environment variables or user input for security.")
    
    st.markdown("""
    ###  What you can do with this app:
    - **Chat**: Ask questions in natural language
    - **Images**: Upload photos and ask questions about them
    - **Videos**: Upload videos and get analysis/descriptions
    - **Mixed**: Combine text, images, and videos in one conversation
    
    ###  Supported formats:
    - **Images**: PNG, JPG, JPEG, GIF, BMP, WebP
    - **Videos**: MP4, MOV, AVI, WMV
    """)
