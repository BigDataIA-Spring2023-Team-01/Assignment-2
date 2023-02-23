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

        
        # check_file_exists
        def check_file_exists(filename, bucket_name):
            try:
                s3client.head_object(Bucket=bucket_name, Key=filename)
                return True
            except Exception as e:
                return False

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
                
                final_url = 'https://{}.s3.amazonaws.com/index.html#{}/{}/{}/{}/{}'.format(bucket,year_nexrad,month_of_year_nexrad,day_of_month_nexrad,selected_stationcode,selected_file)
                name_of_file = selected_file
                if(selected_file != 'select'):
                    if check_file_exists(name_of_file, USER_BUCKET_NAME):
                        st.success(f"The file {name_of_file} already exists in the {USER_BUCKET_NAME} bucket.", icon="✅")

                        st.write('Click to download from S3 bucket', 'https://{}.s3.amazonaws.com/{}'.format(USER_BUCKET_NAME,name_of_file))
                        st.write('Link to file on GEOS website',url_gen_nexrad(name_of_file))
                        timestamp = time.time()
                        log_file_download(name_of_file,timestamp,bucket)
                    else:
                        st.write(f"The file {name_of_file} does not exist in the {USER_BUCKET_NAME} bucket.")
                        transfer_file_to_S3()
                        st.write('Link to file on GEOS website',url_gen_nexrad(name_of_file))



                


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
