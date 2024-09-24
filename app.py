import os
import streamlit as st
from streamlit_chat import message
from model.utils import create_model, setup_logger, generate_content
import google.generativeai as genai
import base64
from settings.base import setup_logger
import json
from datetime import datetime

# Set up logging
logger = setup_logger()

# Initialize session state variables
if 'history' not in st.session_state:
    st.session_state.history = []
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None
if 'model' not in st.session_state:
    st.session_state.model = None

def save_chat_history(user_name, chat_history):
    """
    Save chat history to a file in a user-specific directory with a timestamp.
    """
    base_dir = "chat_history"
    user_dir = os.path.join(base_dir, user_name)
    os.makedirs(user_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(user_dir, f"session_{timestamp}.json")
    
    # Prepare a serializable version of chat_history
    serializable_history = []
    for entry in chat_history:
        if entry['role'] == 'user':
            if len(entry['parts']) > 1:
                uploaded_file = entry['parts'][0]
                user_entry = {
                    'role': 'user',
                    'parts': f"file_api: {uploaded_file}, {entry['parts'][1]}"
                }
            else:
                user_entry = {
                    'role': 'user',
                    'parts': entry['parts'][0]
                }
            serializable_history.append(user_entry)
        elif entry['role'] == 'model':
            model_entry = {
                'role': 'model',
                'parts': entry['parts']
            }
            serializable_history.append(model_entry)
    
    with open(file_path, "w") as f:
        json.dump(serializable_history, f, indent=4)
    
    logger.info(f"Chat history saved to {file_path}")

def conversation_chat(file_path, text_prompt):
    """
    Handle the conversation with the chat session using the provided file path and text prompt.
    """
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        user_input = text_prompt if text_prompt else ""
        
        if file_path:
            temp_file_path = os.path.join(temp_dir, file_path.name)
            with open(temp_file_path, "wb") as f:
                f.write(file_path.read())  # Write the uploaded file to temp location

            logger.info(f"Successfully saved uploaded file: {file_path.name}")
            
            file = genai.upload_file(path=temp_file_path, display_name=temp_file_path)
            user_entry = {
                "role": "user",
                "parts": [file, user_input]
            }
        else:
            user_entry = {
                "role": "user",
                "parts": [user_input]
            }
        
        st.session_state.history.append(user_entry)

        response_text = generate_content(st.session_state.model, st.session_state.history)
            
        bot_entry = {
            "role": "model",
            "parts": response_text
        }
            
        st.session_state.history.append(bot_entry)

        logger.info("Conversation successfully processed")
       
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        st.session_state.history.append("Error")

def display_chat():
    """
    Display chat input and responses.
    """
    st.title("🤖")
    
    chat_container = st.container()
    upload_container = st.container()

    clear_chat_button = st.button('Clear Chat')

    with upload_container:
        with st.form(key='chat_form', clear_on_submit=True):
            file_path = st.file_uploader("Upload", type=["jpg", "jpeg", "png", "mpeg", "mp3", "wav", "ogg", "mp4"])
            text_prompt = st.text_input("Type Here...")
            submit_button = st.form_submit_button(label='Send ⬆️')

    if submit_button:
        conversation_chat(file_path, text_prompt)
    
    if clear_chat_button:
        st.session_state.history = []
        st.session_state.chat_session = None

    with chat_container:
        message(f"Hey there!", avatar_style="bottts")
        for i, entry in enumerate(st.session_state.history):
            if entry['role'] == 'user': 
                if len(entry['parts']) > 1:
                    uploaded_file = entry['parts'][0]
                    base_file_name = os.path.basename(uploaded_file.display_name)
                    if uploaded_file.mime_type.startswith("image/"):
                        file_name = uploaded_file.display_name
                        with open(file_name, "rb") as file:
                            encoded_img = base64.b64encode(file.read()).decode('utf-8')
                        img_html = f'<img src="data:image/png;base64,{encoded_img}" width="200" style="margin-top: 5px;"/>'
                        st.markdown(f"""
                            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                                <div style="max-width: 300px; background-color: #E8E8E8; border-radius: 10px; padding: 10px; position: relative;">
                                    <div style="text-align: right;">
                                        {img_html}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        message(base_file_name, is_user=True, key=f"{i}_user", avatar_style="adventurer")

                    if entry['parts'][1] != "":
                        message(entry['parts'][1], is_user=True, key=f"{i}_user", avatar_style="adventurer")
                else:
                    message(entry['parts'][0], is_user=True, key=f"{i}_user", avatar_style="adventurer")
            elif entry['role'] == 'model':
                message(entry['parts'], key=str(i), avatar_style="bottts")

def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="🤖")

    if st.session_state.model is None:
        st.session_state.model = create_model("AIzaSyAJnWQ8yHqL7CLpJoz9kz2HDSCHFZReGBE", {})

    display_chat()

if __name__ == "__main__":
    main()
