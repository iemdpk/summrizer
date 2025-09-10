import streamlit as st
from component.db import client

def login_page():
    st.title("Login with your email")
    email = st.text_input("Enter email")
    password = st.text_input("Enter Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", type="primary",use_container_width=True):
            result  = client["summryzer"]["auth"].find({"email":email,"password":password})
            result = list(result)
            st.write(result)
            if(len(result) == 1):
                st.session_state.userdata = result[0]
                st.session_state.page = "dashboard"
                st.rerun()

    with col2:
        if st.button("SignUp",use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()
