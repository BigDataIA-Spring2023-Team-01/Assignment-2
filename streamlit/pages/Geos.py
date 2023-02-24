import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import sys
sys.path.insert(1, '../../streamlit')
import boto3
import logging
from dotenv import load_dotenv
import io
import requests
from bs4 import BeautifulSoup
import time
import sys
from goes_db import log_file_download,retieve_year, retieve_day_of_year,retieve_hour
from url_generator import file_validator,url_gen_goes
from login import login

load_dotenv()

s3client = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))




st.header("Explore the GEOS-18 Dataset")

bucket = 'noaa-goes18'
prefix = 'ABI-L1b-RadC/'
USER_BUCKET_NAME = os.environ.get('USER_BUCKET_NAME')


col1, col2 = st.columns(2,gap='large')
if st.session_state['access_token'] != '':
    with col1:
        st.header("Search using fields ")
        #Transfer file to S3 bucket
        def list_files_as_dropdown(bucket_name, prefix):
            try:
                result = s3client.list_objects(Bucket=bucket_name, Prefix=prefix, Delimiter ='/')
                object_list = [x["Key"].split("/")[-1] for x in result["Contents"]]
                return object_list
            except Exception as e:
                st.write("An error occurred:", e)
                return None
            

        #Selecting station 
        station_geos = st.text_input(
            'Please select the station', placeholder= 'GEOS 18')

        #Selecting Year
        year_geos = st.selectbox(
            'Please select the year',
            options=retieve_year())

        #Day of Year
        day_of_year_geos = st.selectbox('Please select the Day of Year', options=retieve_day_of_year(year_geos))

        hour_of_day = st.selectbox(
                    'Please select the Hour',
                    options=retieve_hour(year_geos,day_of_year_geos))

        bucket = 'noaa-goes18'
        prefix = 'ABI-L1b-RadC/{}/{}/{}/'.format(year_geos,day_of_year_geos,hour_of_day)
        object_list = list_files_as_dropdown(bucket, prefix)
        selected_file = st.selectbox("Select file for download:", options =object_list)

        #Transfering selected file to S3 bucket 
        if st.button('Submit'):
            with st.spinner('Retrieving details for the file you selected, wait for it....!'):
                time.sleep(5)

                # final_url = 'https://{}.s3.amazonaws.com/index.html#ABI-L1b-RadC/{}/{}/{}/{}'.format(bucket,year_geos,day_of_year_geos,hour_of_day,selected_file)
                name_of_file = {"filename":str(selected_file)}
            
        
                
                try:
                    url = str(os.environ.get('URL')) + 'transfer_file'
                    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                    response = requests.get(url,headers=headers,params=name_of_file)
                    timestamp = time.time()
                    data = response.json()
                    log_file_download(selected_file,timestamp,bucket)
                    if response.status_code ==  200:
                        st.write("S3 Team Bucket link :",data['S3-Personal'])
                        st.write("S3 Public GOES link :",data['S3-Public'])
                    
                except:
                    st.error("An error occured")
                
                




                

    with col2:
        
        st.header("Search using file name ")
        filename = st.text_input("Enter the filename:")
        json_file_name = {"filename":filename}
        if st.button('Get the Link'):
            try:
                url = os.environ.get('URL') + 'filename_url_gen_goes'
                headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                response = requests.get(url,headers=headers,params=json_file_name)
            except any:
                st.error("An error occured")
            data = response.json()
            if(response.status_code == 200):
                st.write("S3 Public GOES Bucket Link:",data['url'])
            elif(response.status_code == 400):
                st.warning('Filename does not exist')
            elif(response.status_code == 406):
                st.warning('File name format is invalid')

else:
    st.warning("Login First")



