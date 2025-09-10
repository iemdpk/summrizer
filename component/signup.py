import streamlit as st
import time
from component.db import client


def signup_page():

    st.title("Singup")
    username = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    if st.button("Signup with your email",use_container_width=True,type="primary"):
      
        st.success("Signup Successful..")
        time.sleep(2)
        st.info("We are creating your account")
        client["summryzer"]["auth"].insert_one({"email":username,"password":password})
        st.session_state.page = "login"
        st.rerun()
        

