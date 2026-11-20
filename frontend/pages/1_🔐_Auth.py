"""
EduPath AI - Student Authentication
Secure registration and login with bcrypt hashing and JWT tokens.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Authentication", page_icon="🔐", layout="centered")
render_sidebar()

render_header(title="Account Authentication", subtitle="Register a new student account or sign in to your dashboard")

tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])

with tab_login:
    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Sign In", use_container_width=True)

        if submit_login:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Authenticating..."):
                    res = api_client.login(username, password)
                    if res["status_code"] == 200:
                        data = res["data"]
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["refresh_token"] = data["refresh_token"]
                        st.session_state["user"] = {
                            "id": data["user_id"],
                            "username": data["username"],
                            "role": data["role"]
                        }
                        st.success("Successfully logged in! Redirecting...")
                        st.rerun()
                    else:
                        st.error(res["data"].get("detail", "Login failed. Check your credentials."))

with tab_register:
    with st.form("register_form"):
        reg_username = st.text_input("Choose Username (min 3 chars)")
        reg_email = st.text_input("Email Address")
        reg_password = st.text_input("Password (min 8 chars)", type="password")
        reg_confirm = st.text_input("Confirm Password", type="password")
        submit_register = st.form_submit_button("Create Account", use_container_width=True)

        if submit_register:
            if not reg_username or not reg_email or not reg_password:
                st.error("All fields are required.")
            elif len(reg_password) < 8:
                st.error("Password must be at least 8 characters long.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Creating account..."):
                    res = api_client.register(reg_email, reg_username, reg_password)
                    if res["status_code"] == 201:
                        data = res["data"]
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["refresh_token"] = data["refresh_token"]
                        st.session_state["user"] = {
                            "id": data["user_id"],
                            "username": data["username"],
                            "role": data["role"]
                        }
                        st.success("Account created successfully! Welcome to EduPath AI.")
                        st.rerun()
                    else:
                        st.error(res["data"].get("detail", "Registration failed. Please try again."))
