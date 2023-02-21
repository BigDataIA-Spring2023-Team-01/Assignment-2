import streamlit as st
import sqlite3
import hashlib
from jwt import app
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests

# define the Streamlit login page
def login():
    st.title("Login")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    username = st.text_input("Username",key="username")
    password = st.text_input("Password",key="password")
    if st.button("Login"):
        url = "http://localhost:8080/token"
        json_data = {"username": username, "password": password}

        response = requests.post(url,json=json_data)        
        if response.status_code == 200:
            st.success("Logged in as {}".format(username))
            return True # return True after a successful login
        else:
            st.error("Invalid username or password")
    return False

# define the Streamlit main application
def show_main_app():
    st.title("Main Application")
    st.write("Welcome to the main application!")
    # add the rest of your application code here

def show_geos():
    exec(open("streamlit/Geos.py").read())



def main():
    # test()
    if login():
        show_main_app()

if __name__ == "__main__":
    main()
