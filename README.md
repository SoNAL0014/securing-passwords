# VaultX Pro | Symmetric Password Manager

**VaultX Pro** is a high-performance password management dashboard built with Python and Streamlit. Unlike standard hashing scripts, VaultX Pro uses industry-standard symmetric encryption, allowing you to securely store and retrieve your credentials through a centralized GUI.

---

## Quick Start

### 1. Prerequisites

Ensure you have **Python 3.8+** installed. Check your version:

```bash
python --version
```

### 2. Installation

**RECOMMENDED: USE A VIRTUAL ENVIRONMENT(.venv)**

Install the required libraries, including `cryptography` for the encryption engine:

```bash
pip install streamlit pandas cryptography
```

### 3. Running the App

Launch the Streamlit server from your terminal:\

```bash
streamlit run app.py
```

The interface will be available at `http://localhost:8501`.

---

## Key Features

> -**Two-Way Encryption:** Utilizes Fernet (AES-128) symmetric encryption, allowing for secure storage and on-demand retrieval of plaintext passwords.
> -**Master Key System:** Automatically generates a local `master.key` file. Your data remains unreadable without this specific key.
> -**On-the-Fly Decryption:** Passwords remain encrypted within the database and are only decrypted in memory when you choose to view them.
> -**Modern Interface:** A streamlined dark-mode dashboard with sidebar navigation and expandable credential cards.

---

## Project Structure

> -`app.py`: Core application logic and Streamlit UI.
> -`master.key`: **Critical.** This file contains your encryption key. If lost, the vault cannot be decrypted.
> -`vault_encrypted.json`: Your local encrypted database.
> -`README.md`: Documentation and setup guide.

---

## Security Architecture

VaultX Pro implements the **Fernet** specification, which guarantees that a message encrypted using it cannot be manipulated or read without the key. 

**Important Security Practices:**
> -**Backup your Key:** Keep a copy of `master.key` in a separate, secure location.
> -**Local Storage:** Your passwords are saved locally on your machine, not on a cloud server, giving you full sovereignty over your data.
> -**Key Isolation:** Never share your `master.key` file or commit it to public version control (like GitHub).

---

## Built With

> -[Streamlit](https://streamlit.io/) - UI Framework.
> -[Cryptography](https://cryptography.io/) - Secure recipe layer for encryption.
> -[Pandas](https://pandas.pydata.org/) - Data structure management.

---

**Developed for secure and private credential management.**