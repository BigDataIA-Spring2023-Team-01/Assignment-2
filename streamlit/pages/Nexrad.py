import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import boto3
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
import io
import requests
from bs4 import BeautifulSoup
import time

#Custom imports
import nexrad_db,url_generator,goes_db

retieve_days = nexrad_db.retieve_days
retieve_months = nexrad_db.retieve_months
retieve_stations = nexrad_db.retieve_stations

url_gen_nexrad = url_generator.url_gen_nexrad
file_validator_nexrad = url_generator.file_validator_nexrad
log_file_download = goes_db.log_file_download

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
                name_of_file = {"filename":str(selected_file)}
                
                url = str(os.environ.get('URL')) + 'transfer_file_nexrad'
                headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                response = requests.get(url,headers=headers,params=name_of_file)
                data = response.json()
                st.write("S3 Team Bucket link :",data['S3-Personal'])
                st.write("S3 Public GOES link :",data['S3-Public'])

                timestamp = time.time()
                log_file_download(selected_file,timestamp,bucket)
                


    with col2:
        st.header("Search using file name ")
            
        filename = st.text_input("Enter the filename:")
        json_file_name = {"filename":filename}
        if st.button('Get the Link'):
            try:
                url = os.environ.get('URL') + 'filename_url_gen_nexrad'
                headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                response = requests.get(url,headers=headers,params=json_file_name)
            except:
                print("Failed")
            data = response.json()
            if(response.status_code == 200):
                st.write(data['url'])
            elif(response.status_code == 400):
                st.warning('Filename does not exist')
            elif(response.status_code == 406):
                st.warning('File name format is invalid')

            
else:
    st.warning("Login First")
