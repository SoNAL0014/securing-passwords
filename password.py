import streamlit as st
import json
import os
import re
import random
import string
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

# --- PASSWORD STRENGTH ---
def check_password_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1

    if score <= 2: return "Weak", "red"
    elif score <= 4: return "Medium", "orange"
    else: return "Strong", "green"

# --- PASSWORD SUGGESTIONS ---
def get_password_suggestions(password):
    suggestions = []

    if len(password) < 8:
        suggestions.append("Use at least 8 characters")
    if not re.search(r"[A-Z]", password):
        suggestions.append("Add uppercase letter")
    if not re.search(r"[a-z]", password):
        suggestions.append("Add lowercase letter")
    if not re.search(r"[0-9]", password):
        suggestions.append("Add number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        suggestions.append("Add special character")

    return suggestions

# --- PASSWORD GENERATOR ---
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

# --- APP CONFIG ---
st.set_page_config(page_title="VaultX Pro", layout="wide")

st.title("VaultX Pro: Retrievable Manager")
st.sidebar.info("Your Master Key is stored in 'master.key'. Do not lose it!")

menu = ["Add Password", "View Vault", "Recent Passwords"]
choice = st.sidebar.selectbox("Menu", menu)

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

        if st.button("Generate Strong Password"):
            pw = generate_password()
            st.success(f"Generated Password: {pw}")

    # 🔐 Strength + Progress Bar + Suggestions
    if pw:
        strength, color = check_password_strength(pw)

        if strength == "Weak":
            percent = 30
        elif strength == "Medium":
            percent = 65
        else:
            percent = 100

        st.markdown(f"### Password Strength: :{color}[{strength}]")
        st.progress(percent)
        st.write(f"Strength Score: {percent}%")

        if percent < 50:
            st.error("Weak password ⚠️")
        elif percent < 80:
            st.warning("Medium password ⚠️")
        else:
            st.success("Strong password ✅")

        suggestions = get_password_suggestions(pw)
        if suggestions:
            st.warning("To make your password stronger:")
            for s in suggestions:
                st.write(f"• {s}")
        else:
            st.success("No improvements needed")

    # --- SAVE BUTTON ---
    if st.button("Encrypt & Save"):
        if pw == confirm and site and email:

            data = []
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f:
                    data = json.load(f)

            # ❌ DUPLICATE CHECK (BLOCK SAVE)
            duplicate_found = False
            for entry in data:
                if decrypt_password(entry["password"]) == pw:
                    duplicate_found = True
                    break

            if duplicate_found:
                st.error("❌ This password is already used! Try a different one.")
            else:
                new_data = {
                    "site": site,
                    "email": email,
                    "password": encrypt_password(pw),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                data.append(new_data)

                with open(DB_FILE, "w") as f:
                    json.dump(data, f, indent=4)

                st.success(f"Saved credentials for {site}")

        else:
            st.error("Please check your inputs")

# --- VIEW VAULT ---
elif choice == "View Vault":
    st.subheader("Your Vault")

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)

        if data:
            for i, entry in enumerate(data):
                with st.expander(f"{entry['site']} ({entry['email']})"):
                    decrypted_pw = decrypt_password(entry['password'])
                    st.text_input("Password", value=decrypted_pw, key=i)
                    st.write(f"Saved on: {entry['date']}")
        else:
            st.warning("Vault is empty")
    else:
        st.info("No data found")

# --- RECENT PASSWORDS ---
elif choice == "Recent Passwords":
    st.subheader("Recently Added Passwords")

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)

        if data:
            sorted_data = sorted(data, key=lambda x: x["date"], reverse=True)

            for entry in sorted_data[:5]:
                st.write(f"🔹 {entry['site']} ({entry['email']}) - {entry['date']}")
        else:
            st.warning("No recent passwords")
    else:
        st.info("No data available")
