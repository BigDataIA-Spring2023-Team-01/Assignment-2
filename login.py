import streamlit as st
import sqlite3
import hashlib
from .api.jwt import app
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
        url = "http://localhost:8081/token"
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
    # st.title("Main Application")
    # st.write("Welcome to the main application!")
    url = "http://127.0.0.1:8081/users/me/"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNjc3MDI3ODMyfQ.VuRXFA7PKK8srafLP_7KL70CYv5YJNu99hhnmpWFDX4"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    # check response
    if response.status_code == 200:
        print(response.json())
    else:
        print("Request failed with status code:", response.status_code)
        # add the rest of your application code here

def show_geos():
    exec(open("streamlit/Geos.py").read())

def navigate_to_page(page_name):
    query_params = {"page": page_name}
    st.experimental_set_query_params(**query_params)

def main():
    # test()
    if login():
        st.write("Loading")
        # navigate_to_page("streamlit/Geos.py")   
    # show_main_app()

if __name__ == "__main__":
    main()
