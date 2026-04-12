import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import sqlite3
import hashlib
import os
import base64
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Image Captioner", page_icon="📸", layout="wide")

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# --- DATABASE SETUP ---
conn = sqlite3.connect('app_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS history (username TEXT, image_path TEXT, caption TEXT, timestamp TEXT)')
conn.commit()

# --- SECURITY FUNCTIONS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- STYLING ---
def inject_global_styling(image_file, overlay_opacity=0.5, is_login=True):
    """Safely injects CSS to set the background and style components."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_image_path = os.path.join(current_dir, image_file)
        
        with open(full_image_path, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        
        css = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, {overlay_opacity}), rgba(0, 0, 0, {overlay_opacity})), url(data:image/jpeg;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Force ALL typography to white to override Streamlit's light theme */
        h1, h2, h3, h4, h5, h6, p, span, label, div[data-testid="stMarkdownContainer"] > p {{
            color: #FFFFFF !important;
        }}
        
        /* Style info/success boxes so they are dark and readable */
        div[data-testid="stAlert"] {{
            background-color: rgba(30, 30, 40, 0.85) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
        }}
        """

        if is_login:
            css += """
            .block-container {
                background-color: transparent !important;
                padding-top: 3rem !important;
            }
            """
        else:
            css += """
            .block-container {
                background-color: rgba(17, 24, 39, 0.85) !important; 
                padding: 3rem !important;
                border-radius: 15px !important;
                margin-top: 3rem !important;
                margin-bottom: 3rem !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            """

        # Shared input/button styles
        css += """
        .stTextInput > div > div > input {
            background-color: rgba(31, 41, 55, 0.6) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            padding: 12px !important;
        }
        div.stButton > button[kind="primary"] {
            background-color: #3b82f6 !important;
            color: white !important;
            border-radius: 8px !important;
            width: 100% !important;
            border: none !important;
            padding: 10px !important;
            font-weight: bold !important;
            margin-top: 10px !important;
        }
        
        /* FILE UPLOADER VISIBILITY */
        div[data-testid="stFileUploadDropzone"] {
            background-color: rgba(31, 41, 55, 0.6) !important;
            border: 2px dashed rgba(255, 255, 255, 0.4) !important;
            border-radius: 10px !important;
        }
        div[data-testid="stFileUploadDropzone"] button {
            background-color: #3b82f6 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 5px 15px !important;
            font-weight: bold !important;
        }
        div[data-testid="stUploadedFile"] {
            background-color: rgba(31, 41, 55, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError as e:
        st.warning(f"Background image not found at: {e}")

# --- AI MODEL ---
@st.cache_resource
def load_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

# --- SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# ==========================================================
# LOGIN PAGE
# ==========================================================
if not st.session_state['logged_in']:

    inject_global_styling("bg_login.jpg", overlay_opacity=0.25)

    st.markdown("""
    <div style="text-align:center; margin-top:20px;">
        <h1 /b style="font-size:65px; font-weight:800;"></h1>
        <h1 style="
            font-size:100px;
            font-weight:1000;
            margin-top:-25px;
            background: linear-gradient(90deg, #FFFFFF, #000000);
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;">
                Image Captioning AI
        </h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.2,1])

    with col2:
        st.markdown("""
        <div style="
            background: rgba(20,20,30,0.65);
            border-radius: 10px;
            padding: 10px;
            backdrop-filter: blur(14px);
        ">
        <h2 style="text-align:center;">Login</h2>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type='password', key="login_password")

            if st.button("Log In", key="login_btn"):
                c.execute("SELECT * FROM users WHERE username = ?", (username,))
                result = c.fetchone()
                if result and check_hashes(password, result[1]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Incorrect Username or Password.")

        with tab2:
            new_user = st.text_input("Create Username", key="signup_username")
            new_password = st.text_input("Create Password", type='password', key="signup_password")

            if st.button("Create Account", key="signup_btn"):
                if new_user == "" or new_password == "":
                    st.warning("Please fill in all fields.")
                else:
                    c.execute("SELECT * FROM users WHERE username = ?", (new_user,))
                    if c.fetchone():
                        st.error("Username already exists.")
                    else:
                        c.execute("INSERT INTO users VALUES (?, ?)",
                                  (new_user, make_hashes(new_password)))
                        conn.commit()
                        st.success("Account created!")

        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# MAIN APP
# ==========================================================
else:

    inject_global_styling("bg_main.jpg", overlay_opacity=0.25)

    st.sidebar.title(f"👤 {st.session_state['username']}")
    app_mode = st.sidebar.radio("Navigation", ["Generate Captions", "My History"])

    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()

    processor, model = load_model()

    if app_mode == "Generate Captions":
        st.title("📸 AI Image Captioning")
        st.markdown("Upload an image, and the AI will generate a caption.")

        # --- THE NEW CAMERA INTEGRATION ---
        input_method = st.radio("Select Input Method:", ["📁 Upload File", "📷 Take Picture"], horizontal=True)
        st.markdown("<br>", unsafe_allow_html=True)

        image_source = None
        
        if input_method == "📁 Upload File":
            image_source = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        else:
            image_source = st.camera_input("Take a picture with your camera")

        # If either an upload or a camera snapshot is provided, process it
        if image_source is not None:
            raw_image = Image.open(image_source).convert('RGB')

            col1, col2 = st.columns(2)

            with col1:
                st.image(raw_image, use_container_width=True)

            with col2:
                with st.spinner("Generating caption..."):
                    inputs = processor(raw_image, return_tensors="pt")
                    with torch.no_grad():
                        out = model.generate(**inputs, max_new_tokens=50)

                    caption = processor.decode(out[0], skip_special_tokens=True).capitalize()

                st.success("Generated Caption:")
                st.write(f"### {caption}")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"uploads/{st.session_state['username']}_{timestamp}.jpg"
                raw_image.save(image_filename)

                c.execute("INSERT INTO history VALUES (?, ?, ?, ?)",
                          (st.session_state['username'], image_filename, caption, timestamp))
                conn.commit()

    elif app_mode == "My History":
        st.title("My Caption History")

        c.execute("SELECT image_path, caption, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC",
                  (st.session_state['username'],))
        records = c.fetchall()

        for record in records:
            img_path, caption, timestamp = record
            try:
                st.image(img_path, use_container_width=True)
                st.write(f"**Caption:** {caption}")
                st.divider()
            except:
                st.error("Image missing.")
