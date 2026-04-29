import streamlit as st
import pandas as pd
import json
import os
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

# Initialize Cipher
cipher = Fernet(load_or_create_key())

def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(token):
    return cipher.decrypt(token.encode()).decode()

# --- APP CONFIG ---
st.set_page_config(page_title="VaultX Pro", page_icon="", layout="wide")

# --- UI LOGIC ---
st.title("VaultX Pro: Retrievable Manager")
st.sidebar.info("Your Master Key is stored in 'master.key'. Do not lose this file, or your passwords are gone forever!")

menu = ["Add Password", "View Vault"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Password":
    with st.container():
        st.subheader("Store New Credentials")
        col1, col2 = st.columns(2)
        
        with col1:
            site = st.text_input("Website/App")
            email = st.text_input("Email/Username")
        with col2:
            pw = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")

        if st.button("Encrypt & Save"):
            if pw == confirm and site and email:
                new_data = {
                    "site": site,
                    "email": email,
                    "password": encrypt_password(pw),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                # Load existing
                data = []
                if os.path.exists(DB_FILE):
                    with open(DB_FILE, "r") as f:
                        data = json.load(f)
                
                data.append(new_data)
                with open(DB_FILE, "w") as f:
                    json.dump(data, f, indent=4)
                
                st.success(f"Successfully locked credentials for {site}!")
            else:
                st.error("Please check your inputs.")

elif choice == "View Vault":
    st.subheader("Your Encrypted Vault")
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        
        if data:
            for i, entry in enumerate(data):
                with st.expander(f"🌐 {entry['site']} ({entry['email']})"):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        # We decrypt only when the user expands the section
                        decrypted_pw = decrypt_password(entry['password'])
                        st.text_input(f"Password for {entry['site']}", value=decrypted_pw, type="default", key=f"pw_{i}")
                    with col_b:
                        st.write(f"Saved on: \n{entry['date']}")
        else:
            st.warning("Vault is empty.")
    else:
        st.info("No vault found yet.")