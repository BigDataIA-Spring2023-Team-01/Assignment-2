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
        def check_file_exists(filename, bucket_name):
            try:
                s3client.head_object(Bucket=bucket_name, Key=filename)
                return True
            except Exception as e:
                return False


        def get_file_url(year, day_of_year, hour,selected_file):
            # Base URL of the GEOS website
            base_url = "https://noaa-goes18.s3.amazonaws.com/ABI-L1b-RadC/"
            
            # Year, day of year, and hour are formatted as strings with leading zeros
            year = str(year).zfill(4)
            day_of_year = str(day_of_year).zfill(3)
            hour = str(hour).zfill(2)
            
            # Combine the base URL with the user inputs to get the file URL
            file_url = base_url + f"{year}/{day_of_year}/{hour}/{selected_file}"
            
            st.write("Link to file on GEOS website ",file_url) 


        #Transfer file to S3 bucket
        def transfer_file_to_S3():
            try:
                
                st.write("Uploading the file to S3 bucket for download...")
                with open(selected_file, "wb") as data:
                    data.write(requests.get(final_url).content)
                    s3client.upload_file(selected_file, USER_BUCKET_NAME, name_of_file)
                    with st.spinner('Almost there...'):
                        time.sleep(5)
                        st.success('File was successfully uploaded!', icon="✅")
                st.write('Click to download from S3 bucket', 'https://{}.s3.amazonaws.com/{}'.format(USER_BUCKET_NAME,name_of_file))
            except Exception as e:
                st.write("An error occurred:", str(e))

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

                final_url = 'https://{}.s3.amazonaws.com/index.html#ABI-L1b-RadC/{}/{}/{}/{}'.format(bucket,year_geos,day_of_year_geos,hour_of_day,selected_file)
                name_of_file = selected_file
            
        
                if(selected_file != 'select'):
                    if check_file_exists(name_of_file, USER_BUCKET_NAME):
                        st.success(f"The file {name_of_file} already exists in the {USER_BUCKET_NAME} bucket.", icon="✅")
                        st.write('Click to download from S3 bucket', 'https://{}.s3.amazonaws.com/{}'.format(USER_BUCKET_NAME,name_of_file))
                        get_file_url(year_geos,day_of_year_geos,hour_of_day,selected_file)
                        timestamp = time.time()
                        log_file_download(name_of_file,timestamp,bucket)

                    else:
                        st.write(f"The file {name_of_file} does not exist in the S3: {USER_BUCKET_NAME} bucket.")
                        transfer_file_to_S3()
                        get_file_url(year_geos,day_of_year_geos,hour_of_day,selected_file)

    with col2:
        
        st.header("Search using file name ")
        
        filename = st.text_input("Enter the filename:")
        if filename:
            url = 'http://localhost:8080/filename_url_gen_nexrad'
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.get(url,headers=headers)
            st.write(response.json())


else:
    st.warning("Login First")



