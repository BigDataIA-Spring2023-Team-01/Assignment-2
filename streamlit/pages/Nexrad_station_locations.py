import streamlit as st
import pandas as pd
import requests

endpoint_url = "http://10.0.0.17:8000/coordinatesdata"

def get_coordinate_data():
    response = requests.get(endpoint_url)
    data = response.json()
    return (data)

st.title("Points of all NEXRAD Doppler radars")
df = pd.DataFrame(get_coordinate_data())
st.map(df)
