import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import os
load_dotenv()

url = os.environ.get('URL') + 'coordinatesdata'

if st.session_state['access_token'] != '':

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    response = requests.get(url,headers=headers)
    data = response.json()
    if response.status_code == 200:
        st.title("Points of all NEXRAD Doppler radars")
        df = pd.DataFrame(data)
        st.map(df)
    else:
        st.write("Error while loading data for doppler plot")


else:
    st.warning("Login First")
    