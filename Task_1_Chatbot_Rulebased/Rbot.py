import os
import re
import random
import sys
import streamlit as st
import base64

# --- Function to set local image as background ---
def set_background(image_file):
    # This forces Python to look in the same folder as Rbot.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, image_file)

    if not os.path.exists(image_path):
        st.error(f"Could not find {image_file}. I looked exactly here: {image_path}")
        return

    # Open using the new exact path
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        /* 1. Set the background image */
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 2. Add text shadows so text is readable over the bright image */
        h1, h2, h3, p, span {{
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
        }}

        /* 3. Make chat input box semi-transparent dark */
        .stChatInputContainer {{
            background-color: rgba(0, 0, 0, 0.6) !important;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        /* 4. Keep sidebar solid dark */
        [data-testid="stSidebar"] {{
            background-color: #111A24;
        }}
        
        /* 5. Keep the sidebar clear chat button visible */
        .stButton > button {{
            background-color: rgba(255, 255, 255, 0.1); 
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        .stButton > button:hover {{
            background-color: rgba(255, 255, 255, 0.2);
            border: 1px solid white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


class Rbot:
    def __init__(self):
        self.rules = {
            r'.*(hi|hello|hey|hola|hai).*': [
                "Hello! I'm Rbot. How can I help you today?",
                "Hey there! Ready to chat?",
                "Hi! What's on your mind?"
            ],
            r'.*how are you.*': [
                "I'm functioning at 100% efficiency! How about you?",
                "Doing great, just hanging out in your processor.",
                "I'm good! Thanks for asking."
            ],
            r'.*(name|who are you).*': [
                "I am Rbot, a rule-based AI built in Python.",
                "You can call me Rbot. I'm your local chatbot."
            ],
            r'.*(weather|outside).*': [
                "I don't have a window, but I hope it's sunny!",
                "I'm not connected to a weather API yet, but it's always 72°F in this terminal."
            ],
            r'.*(bye|exit|quit|stop).*': [
                "Goodbye! Have a great day.",
                "See you later!",
                "System shutting down. Farewell!"
            ],
            r'.*(help|can you do).*': [
                "I can chat with you, tell you my name, or just keep you company!",
                "Try asking me 'How are you?' or 'What is your name?'"
            ]
        }
        self.default_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "Focusing... could you say that again?",
        ]

    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        
        for pattern, responses in self.rules.items():
            if re.match(pattern, user_input):
                return random.choice(responses)
        
        return random.choice(self.default_responses)

st.set_page_config(page_title="Rule-Based Bot", page_icon="🤖", layout="centered")

set_background("image_1.png")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100) # Placeholder logo
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("Rule-Based Chatbot")
st.caption("⚡ Powered by Rule-Based Logic")
st.markdown("---")

if "bot" not in st.session_state:
    st.session_state.bot = Rbot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    st.chat_message("user").markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = st.session_state.bot.get_response(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
