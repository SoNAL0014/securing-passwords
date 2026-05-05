import streamlit as st
import pandas as pd
import json
import os
import re
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime

# --- FILES ---
KEY_FILE = "master.key"
DB_FILE = "vault_encrypted.json"
MASTER_FILE = "master.hash"

# --- MASTER PASSWORD FUNCTIONS ---
def hash_master(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_master_password(password):
    with open(MASTER_FILE, "w") as f:
        f.write(hash_master(password))

def verify_master_password(password):
    if not os.path.exists(MASTER_FILE):
        return False
    with open(MASTER_FILE, "r") as f:
        stored_hash = f.read()
    return stored_hash == hash_master(password)

# --- ENCRYPTION SETUP ---
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

# --- PASSWORD STRENGTH CHECK ---
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

# --- SESSION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- FIRST TIME MASTER PASSWORD SETUP ---
if not os.path.exists(MASTER_FILE):
    st.title("🔐 Set Master Password")
    
    new_pass = st.text_input("Create Master Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Set Password"):
        if not new_pass or not confirm_pass:
            st.error("Please fill both fields.")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            save_master_password(new_pass)
            st.success("Master password set successfully! Restart the app.")
    
    st.stop()

# --- LOGIN ---
if not st.session_state.authenticated:
    st.title("🔐 Vault Login")
    
    master_input = st.text_input("Enter Master Password", type="password")

    if st.button("Login"):
        if verify_master_password(master_input):
            st.session_state.authenticated = True
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Incorrect password ❌")

    st.stop()

# --- APP CONFIG ---
st.set_page_config(page_title="VaultX Pro", page_icon="🔒", layout="wide")

st.title("VaultX Pro: Secure Password Manager")

# --- SIDEBAR ---
menu = ["Add Password", "View Vault"]
choice = st.sidebar.selectbox("Menu", menu)

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.info("Keep your master.key file safe!")

# --- ADD PASSWORD ---
if choice == "Add Password":
    st.subheader("Store New Credentials")
    
    col1, col2 = st.columns(2)
    with col1:
        site = st.text_input("Website/App")
        email = st.text_input("Email/Username")
    
    with col2:
        pw = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

    # Strength meter
    if pw:
        strength_score, suggestions = check_password_strength(pw)
        levels = ["Very Weak", "Weak", "Medium", "Strong", "Excellent"]

        st.markdown(f"**Strength: {levels[min(strength_score, 4)]}**")
        st.progress(strength_score / 5)

        if suggestions:
            st.caption(f"Improve by adding: {', '.join(suggestions)}")

        if strength_score == 5:
            st.success("💪 Password is 100% strong")
        else:
            st.error("⚠️ Must be 100% strong to save")

    # SAVE BUTTON
    if st.button("Encrypt & Save"):
        if not pw or not site or not email:
            st.error("Please fill all fields.")
        elif pw != confirm:
            st.error("Passwords do not match.")
        else:
            strength_score, suggestions = check_password_strength(pw)

            if strength_score < 5:
                st.error("❌ Password NOT saved. It is not strong enough.")
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
                
                st.success(f"✅ Credentials for {site} saved securely.")

# --- VIEW VAULT ---
elif choice == "View Vault":
    st.subheader("Your Encrypted Vault")
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
        
        if data:
            for i, entry in enumerate(data):
                with st.expander(f"{entry['site']} | {entry['email']}"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        decrypted_pw = decrypt_password(entry['password'])
                        st.text_input("Password", value=decrypted_pw, key=f"v_{i}")
                    with c2:
                        st.write(f"Created: {entry['date']}")
        else:
            st.info("Vault is empty.")
    else:
        st.info("No vault found.")
