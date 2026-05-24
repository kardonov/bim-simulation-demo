import streamlit as st
import hashlib
from utils.db import query, execute


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def init_session():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = {}
    if "page" not in st.session_state:
        st.session_state["page"] = "login"


def login_user(email, password):
    if not email or not password:
        return False, "Email dan password wajib diisi."
    row = query("SELECT id, email, name, role, nim_nidn, program_study, semester FROM users WHERE email=? AND password=?",
                (email, hash_pw(password)), fetchone=True)
    if row:
        st.session_state["logged_in"] = True
        st.session_state["user"] = {
            "id": row[0], "email": row[1], "name": row[2],
            "role": row[3], "nim_nidn": row[4],
            "program_study": row[5], "semester": row[6],
        }
        st.session_state["page"] = "dashboard"
        return True, "Login berhasil"
    return False, "Email atau password salah."


def register_user(email, password, name, role, nim_nidn, program, semester):
    existing = query("SELECT id FROM users WHERE email=?", (email,), fetchone=True)
    if existing:
        return False, "Email sudah terdaftar."
    try:
        execute(
            "INSERT INTO users (email, password, name, role, nim_nidn, program_study, semester) VALUES (?,?,?,?,?,?,?)",
            (email, hash_pw(password), name, role, nim_nidn, program, semester)
        )
        return True, "Akun berhasil dibuat"
    except Exception as e:
        return False, str(e)


def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["user"] = {}
    st.session_state["page"] = "login"
