import streamlit as st
import pandas as pd
import json
import os
import re
from cryptography.fernet import Fernet
from datetime import datetime

# --- ENCRYPTION SETUP ---
KEY_FILE = "master.key"
DB_FILE = "vault_encrypted.json"

def load_or_create_key():
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE, "rb").read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

cipher = Fernet(load_or_create_key())

def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(token):
    return cipher.decrypt(token.encode()).decode()

# --- STRENGTH CHECKER LOGIC ---
def check_password_strength(password):
    score = 0
    remarks = []
    
    if len(password) >= 8: score += 1
    else: remarks.append("At least 8 characters")
    
    if re.search("[A-Z]", password): score += 1
    else: remarks.append("Uppercase letter")
    
    if re.search("[a-z]", password): score += 1
    else: remarks.append("Lowercase letter")
    
    if re.search("[0-9]", password): score += 1
    else: remarks.append("Number")
    
    if re.search("[@#$%^&*!]", password): score += 1
    else: remarks.append("Special character")
    
    return score, remarks

# --- APP CONFIG ---
st.set_page_config(page_title="VaultX Pro", page_icon="🔒", layout="wide")

# --- UI LOGIC ---
st.title("VaultX Pro: Retrievable Manager")
st.sidebar.info("Master Key: 'master.key'. Keep this file safe to retain access to your data.")

menu = ["Add Password", "View Vault"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Password":
    st.subheader("Store New Credentials")
    
    col1, col2 = st.columns(2)
    with col1:
        site = st.text_input("Website/App", placeholder="e.g. Google")
        email = st.text_input("Email/Username")
    
    with col2:
        pw = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

    # Strength Meter UI
    if pw:
        strength_score, suggestions = check_password_strength(pw)
        strength_levels = ["Very Weak", "Weak", "Medium", "Strong", "Excellent"]
        
        # Color coding
        colors = ["#ff4b4b", "#ff754b", "#ffa54b", "#29b09d", "#00cc96"]
        current_color = colors[strength_score - 1] if strength_score > 0 else colors[0]
        
        st.markdown(f"**Strength: {strength_levels[min(strength_score, 4)]}**")
        st.progress(strength_score / 5)
        
        if suggestions:
            st.caption(f"To improve, add: {', '.join(suggestions)}")

    if st.button("Encrypt & Save"):
        if not pw or not site or not email:
            st.error("Please fill in all fields.")
        elif pw != confirm:
            st.error("Passwords do not match.")
        else:
            new_data = {
                "site": site,
                "email": email,
                "password": encrypt_password(pw),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            data = []
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f:
                    data = json.load(f)
            
            data.append(new_data)
            with open(DB_FILE, "w") as f:
                json.dump(data, f, indent=4)
            
            st.success(f"Credentials for {site} saved securely.")

elif choice == "View Vault":
    st.subheader("Your Encrypted Vault")
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
        
        if data:
            for i, entry in enumerate(data):
                with st.expander(f"{entry['site']} | {entry['email']}"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        decrypted_pw = decrypt_password(entry['password'])
                        st.text_input("Decrypted Password", value=decrypted_pw, type="default", key=f"v_{i}")
                    with c2:
                        st.write(f"Created: {entry['date']}")
        else:
            st.info("Vault is currently empty.")
    else:
        st.info("No vault file found.")