import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import boto3
import logging
from dotenv import load_dotenv
import io
import requests
from bs4 import BeautifulSoup
import time
from nexrad_db import retieve_days,retieve_months,retieve_stations
from url_generator import url_gen_nexrad,file_validator_nexrad
from goes_db import log_file_download
from fastapi import HTTPException
# from IPython.core.display import display, HTML
load_dotenv()

st.header("Explore the NEXRAD Dataset")

s3client = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

bucket = 'noaa-nexrad-level2'

prefix = 'ABI-L1b-RadC/'
USER_BUCKET_NAME = os.environ.get('USER_BUCKET_NAME')

col1, col2 = st.columns(2, gap = 'large')
if st.session_state['access_token'] != '':
    with col1:
        st.header("Search using fields ")


            
        def list_files_as_dropdown(bucket_name, prefix):
            try:
                result = s3client.list_objects(Bucket=bucket_name, Prefix=prefix, Delimiter ='/')
                object_list = [x["Key"].split("/")[-1] for x in result["Contents"]]
                return object_list
            except Exception as e:
                st.write("An error occurred:", e)
                return None

        #Selecting Year
        year_nexrad = st.selectbox(
            'Please select the year',
            ('2022', '2023'))
        
        #Month of Year
        month_of_year_nexrad = st.selectbox('Please select the Month',options=retieve_months(year_nexrad))

        #Day of Month
        day_of_month_nexrad = st.selectbox('Please select the Day of the month',options=retieve_days(year_nexrad,month_of_year_nexrad))

    

        #Station code selector 
        
        selected_stationcode = st.selectbox('Please select the station',options=retieve_stations(year_nexrad,month_of_year_nexrad,day_of_month_nexrad),key='day')



        #MADE CHANGES TO BELOW FUNCTION - ADDED PREFIX_FILE 
        prefix_file = '{}/{}/{}/{}/'.format(year_nexrad,month_of_year_nexrad,day_of_month_nexrad,selected_stationcode)
        bucket = 'noaa-nexrad-level2'


        #Filename selector 
        object_list = list_files_as_dropdown(bucket, prefix_file)
        if(object_list != None):
            selected_file = st.selectbox("Select file for download:", object_list,key='file')


        #Transfering selected file to S3 bucket 
        if st.button('Submit'):
            with st.spinner('Retrieving details for the file you selected, wait for it....!'):
                time.sleep(5)
                name_of_file = {"filename":selected_file}
                if(selected_file != 'select'):
                    try:
                        url = 'http://localhost:8080/transfer_file_nexrad'
                        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                        response = requests.get(url,headers=headers,params=name_of_file)
                        st.write(response.json)
                    except any:
                        print("Failed")
                    timestamp = time.time()
                    log_file_download(selected_file,timestamp,bucket)
                    st.write(f"The file {name_of_file} does not exist in the {USER_BUCKET_NAME} bucket.")
                



                


    with col2:
        st.header("Search using file name ")
            
        filename = st.text_input("Enter the filename:")
        json_file_name = {"filename":filename}
        if st.button('Get the Link'):
            try:
                url = 'http://localhost:8080/filename_url_gen_nexrad'
                headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                response = requests.get(url,headers=headers,params=json_file_name)
            except any:
                print("Failed")

            if(response.status_code == 200):
                st.write(response.json()['url'])
            elif(response.status_code == 400):
                st.warning('Filename does not exist')
            elif(response.status_code == 406):
                st.warning('File name format is invalid')

            
else:
    st.warning("Login First")
