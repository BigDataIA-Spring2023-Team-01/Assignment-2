import streamlit as st
import sqlite3
import hashlib
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests
from fastapi import Form
# define the Streamlit login page
from pydantic import BaseModel
import os

st.session_state['access_token']= ''

class Login:
    username:str = Form()
    password:str = Form()

def login():
    st.title("Login")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    username = st.text_input("Username",key="username")
    password = st.text_input("Password",type="password",key="password")
    if st.button("Login"):
        url = str(os.environ.get('URL')) + "token"
        response = requests.post(url,data={"username": username, "password": password})        
        if response.status_code == 200:
            res = response.json()
            access_token = res['access_token']
            st.session_state['access_token'] = access_token
            st.success("Logged in as {}".format(username))
            st.write(type(access_token))
            return True # return True after a successful login
        else:
            st.error("Invalid username or password")
    return False

# define the Streamlit main application
def show_main_app():
    # st.title("Main Application")
    # st.write("Welcome to the main application!")
    url = "http://localhost:8080/users/me"
    #token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNjc3MTI5MTgwfQ.71FkTnZBGyLT1fbz0E0WQMMVFz2H_0injbiTZLVHBS0"
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    response = requests.get(url, headers=headers)

    # check response
    if response.status_code == 200:
        print(response.json())
    else:
        print("Request failed with status code:", response.status_code)
        # add the rest of your application code here




def main():
    if login():
        print("great")


if __name__ == "__main__":
    main()
