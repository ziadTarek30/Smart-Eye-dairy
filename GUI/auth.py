import time
import streamlit as st
import json
import os
import random
import smtplib
from email.message import EmailMessage
import hashlib
from PIL import Image
import base64
from io import BytesIO


def add_bg_logo():
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                img = Image.open(f)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                st.markdown(
                    f"""
                    <style>
                        .stApp {{
                            background-image: url("data:image/png;base64,{img_str}");
                            background-size: 500px;
                            background-repeat: no-repeat;
                            background-position: center;
                            background-attachment: fixed;
                        }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
        except Exception as e:
            st.warning(f"Couldn't load background logo: {e}")

users_file = "users.json"
OTP_CODE = None

def load_users():
    if os.path.exists(users_file):
        try:
            with open(users_file, "r") as f:
                data = f.read()
                if not data.strip():  # Handle empty file
                    return {}
                users = json.loads(data)
                # Convert old format (str) to new format (dict)
                if users and isinstance(next(iter(users.values())), str):
                    return {email: {'password': pwd} for email, pwd in users.items()}
                return users
        except json.JSONDecodeError:
            return {}
    return {}

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(plain, hashed):
    return hash_password(plain) == hashed

def send_otp(recipient_email, subject="OTP Verification"):
    # Get API key from user data
    users = load_users()
    
    # Check if recipient_email exists in users (not session state)
    if recipient_email not in users:
        st.error("User not found")
        return None
    
    # Get sender credentials from the recipient's user data
    user_data = users[recipient_email]
    sender_email = user_data.get('email', '')
    sender_pass = user_data.get('api_key', '')
    
    if not sender_email or not sender_pass:
        st.error("Sender credentials not configured")
        return None
    
    otp = str(random.randint(100000, 999999))
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content(f"Your OTP is: {otp}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_pass)
            server.send_message(msg)
        return otp
    except Exception as e:
        st.error(f"❌ Failed to send OTP: {e}")
        return None

def login_ui():
    add_bg_logo()
    st.title(" Login")

    users = load_users()

    email = st.text_input(" Email", key="login_email_input")
    password = st.text_input(" Password", type="password", key="login_password_input")

    global OTP_CODE
    col1, col2, col3 = st.columns([5, 1, 1])
    
    with col1:
        if st.button("Send OTP to Login "):
            if email in users:
                user_data = users[email]
                stored_password = user_data.get('password', '')
                
                if check_password(password, stored_password):
                    st.session_state.login_email = email
                    st.session_state.login_pass = password
                    
                    OTP_CODE = send_otp(email, "Login OTP")
                    if OTP_CODE:
                        st.session_state.login_otp_sent = True
                        st.success("✅ OTP sent to your email.")
                else:
                    st.error("❌ Invalid email or password")
            else:
                st.error("❌ Invalid email or password")
        
        # Move Debug Login button HERE (inside col1)
        if st.button("Debug Login"):
            st.session_state.logged_in = True
            st.session_state.email = "Debugger@email.com"
            st.success("✅ Login successful!")
            st.rerun()

    if st.session_state.get("login_otp_sent"):
        login_otp_input = st.text_input("🔢 Enter OTP for Login", key="otp_login")
        if st.button("Login"):
            if login_otp_input == OTP_CODE:
                st.session_state.logged_in = True
                st.session_state.email = st.session_state.login_email
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect OTP")

    with col2:
        st.markdown("Don't have an account?")
    with col3:
        if st.button("Go to Register →"):
            st.session_state.page = "Register"
            st.rerun()
    

    
def register_ui():
    add_bg_logo()
    st.title(" Register")

    users = load_users()
    reg_email = st.text_input(" New Supervisor Email", key="reg_email")
    reg_pass = st.text_input(" New Supervisor Password", type="password", key="reg_pass")
    reg_api_key = st.text_input(" Gmail API Key", type="password", key="reg_api_key")
    reg_sender_email = st.text_input(" Sender Gmail Address", key="reg_sender_email")
    
    col1, col2, col3 = st.columns([4, 1, 1])
    
    # First registration (no users exist)
    if not users:
        if st.button("Register First Supervisor"):
            if reg_email and reg_pass and reg_api_key and reg_sender_email:
                users[reg_email] = {
                    'password': hash_password(reg_pass),
                    'api_key': reg_api_key,
                    'email': reg_sender_email
                }
                save_users(users)
                st.success("✅ First supervisor registered successfully!")
                st.session_state.logged_in = True
                st.session_state.email = reg_email
                st.rerun()
            else:
                st.warning("⚠️ Please complete all fields")
    else:
        # Subsequent registrations (require OTP)
        old_email = list(users.keys())[0]
        with col1:
            if st.button("Send OTP to Current Supervisor Email"):
                if old_email in users:
                    # Handle both old and new user formats
                    user_data = users[old_email]
                    api_key = user_data if isinstance(user_data, str) else user_data.get('api_key', '')
                    sender_email = user_data if isinstance(user_data, str) else user_data.get('email', '')
                    
                    if api_key and sender_email:
                        OTP_CODE = send_otp(old_email, "Supervisor Replacement OTP")
                        if OTP_CODE:
                            st.session_state["reg_otp_sent"] = True
                            st.session_state["reg_otp_code"] = OTP_CODE
                            st.success(f"✅ OTP sent successfully to current supervisor ({old_email})")
                    else:
                        st.warning("⚠️ Current supervisor credentials not configured properly")

        if st.session_state.get("reg_otp_sent"):
            reg_otp_input = st.text_input("🔢 Enter OTP to Confirm Replacement", key="otp_register")
            if st.button("Confirm & Register New Supervisor"):
                if reg_otp_input == st.session_state.get("reg_otp_code"):
                    if reg_email and reg_pass and reg_api_key and reg_sender_email:
                        users.clear()
                        users[reg_email] = {
                            'password': hash_password(reg_pass),
                            'api_key': reg_api_key,
                            'email': reg_sender_email
                        }
                        save_users(users)
                        st.success("✅ New supervisor registered successfully and old supervisor removed.")
                        st.session_state.reg_otp_sent = False
                        st.session_state.logged_in = True
                        st.session_state.email = reg_email
                        st.rerun()
                    else:
                        st.warning(" Please complete all fields before confirming.")
                else:
                    st.error(" Incorrect OTP")
    
    with col2:
        st.markdown("Already have an account?")
    with col3:
        if st.button("← Back to Login"):
            st.session_state.page = "Login"
            st.rerun()