import boto3
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import time
import sys
import os
import streamlit as st
import re
import sqlite3
import requests
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from urllib.parse import quote
from typing import Dict, Any
import api.jwt
jwt = api.jwt
User = jwt.User
get_current_active_user = jwt.get_current_active_user


router_file_url_generator = APIRouter()

clientlogs = boto3.client('logs',
                        region_name= 'us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

s3client = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

bucket = 'noaa-goes18'
prefix = 'ABI-L1b-RadC/'
USER_BUCKET_NAME = os.environ.get('USER_BUCKET_NAME')
def write_logs(message: str):
    clientlogs.put_log_events(
    logGroupName =  "Assignment_1",
    logStreamName = "URL_GEN",
    logEvents= [
        {
            'timestamp' : int(time.time() * 1e3),
            'message' : message,
        }
    ]   
)   

#NEXRAD
def check_file_in_S3public_nexrad(filename: str):
    
    arr = filename.split("_")[0]
    year, day, hour, station = arr[4:8], arr[8:10], arr[10:12], arr[0:4]
    fs = "https://noaa-nexrad-level2.s3.amazonaws.com/{}/{}/{}/{}/{}".format(year,day,hour,station,filename)
    # write_logs(fs)
    # return fs
    
    response = requests.get(fs)
    if response.status_code == 200:
        return True
    return False


def url_gen_goes(input):
    write_logs(message="url_generator_starts")
    arr = input.split("_")
    tproduct_code = arr[1].split("-")
    s1 = tproduct_code[2]
    finalProductCode =tproduct_code[0]+"-"+tproduct_code[1]+"-"+ ''.join([i for i in s1 if not i.isdigit()])
    write_logs(finalProductCode)
    date = arr[3]
    year, day_of_year, hour = date[1:5], date[5:8], date[8:10]
    fs = "https://noaa-goes18.s3.amazonaws.com/{}/{}/{}/{}/{}".format(finalProductCode,year,day_of_year,hour,input)
    write_logs(fs)
    return fs

#GEOS
def check_file_in_S3public_geos(filename: str):
        # write_logs(message="url_generator_starts")
        arr = filename.split("_")
        tproduct_code = arr[1].split("-")
        s1 = tproduct_code[2]
        finalProductCode =tproduct_code[0]+"-"+tproduct_code[1]+"-"+ ''.join([i for i in s1 if not i.isdigit()])
        # write_logs(finalProductCode)
        date = arr[3]
        year, day_of_year, hour = date[1:5], date[5:8], date[8:10]
        fs = "https://noaa-goes18.s3.amazonaws.com/{}/{}/{}/{}/{}".format(finalProductCode,year,day_of_year,hour,filename)
  
        response = requests.head(fs)
        if response.status_code == 200:
            return True
        else:
            return False
            
@router_file_url_generator.get("/filename_url_gen_goes")
def filename_url_gen_goes(filename: str):
    # define the expected format for the file name
    expected_format = "OR_ABI-L1b-RadC-M6C01_G18_s{year}{day}{hour}{time}_{end_time}_c{creation_time}.nc"

    
# split the file name into different parts
    file_parts = filename.split("_")
    if len(file_parts) == 6 and file_parts[0] == "OR" and file_parts[1] == "ABI-L1b-RadC-M6C01" and file_parts[2] == "G18":
        year = file_parts[3][1:5]
        day = file_parts[3][5:8]
        hour = file_parts[3][8:10]
        time = file_parts[3][10:]
        end_time = file_parts[4]
        creation_time = file_parts[5][1:-3]

        # if filename not in check_file:
        #     raise HTTPException(status_code=400, detail= "Filename does not exist" ) 
        url = expected_format.format(year=year, day=day, hour=hour,time = time, end_time=end_time, creation_time=creation_time)
        if url == filename:     
            if check_file_in_S3public_geos(filename):
                url_file = url_gen_goes(url)
                return {"url": url_file}
            else:
                raise HTTPException(status_code=400, detail= "Filename does not exist" ) 

    else:
        raise HTTPException(status_code=406, detail= "Invalid filename" )
    #HERE FILENAME DOES NOT EXIST IS NOT WORKING

    

@router_file_url_generator.get("/filename_url_gen_nexrad")
def filename_url_gen_nexrad(filename: str) -> Dict[str, Any]:

    # expected_format = "{nexrad_station}{year}{month}{day}_{time}_V06"
    pattern = r'^\w{4}\d{8}_\d{6}(?:_V06|_V03)?(?:\.gz)?$'
    if re.match(pattern, filename):
        arr = filename.split("_")[0]
        year, day, hour, station = arr[4:8], arr[8:10], arr[10:12], arr[0:4]
        fs = "https://noaa-nexrad-level2.s3.amazonaws.com/{}/{}/{}/{}/{}".format(year,day,hour,station,filename)

        check = check_file_in_S3public_nexrad(filename)
        if check:
            return {"url": fs} 
        else:
            raise HTTPException(status_code=400, detail= "Filename does not exist" ) 
            
    else:
        raise HTTPException(status_code=406, detail= "Invalid filename" )

  



@router_file_url_generator.get('/url_generator_geos')
def url_gen_goes(input:str):
    # write_logs(message="url_generator_starts")
    arr = input.split("_")
    tproduct_code = arr[1].split("-")
    s1 = tproduct_code[2]
    finalProductCode =tproduct_code[0]+"-"+tproduct_code[1]+"-"+ ''.join([i for i in s1 if not i.isdigit()])
    # write_logs(finalProductCode)
    date = arr[3]
    year, day_of_year, hour = date[1:5], date[5:8], date[8:10]
    fs = "https://noaa-goes18.s3.amazonaws.com/{}/{}/{}/{}/{}".format(finalProductCode,year,day_of_year,hour,input)
    # write_logs(fs)
    return {"url":fs}



@router_file_url_generator.get('/url_generator_nexrad')
def url_gen_nexrad(input):
    arr = input.split("_")[0]
    year, day, hour, station = arr[4:8], arr[8:10], arr[10:12], arr[0:4]
    fs = "https://noaa-nexrad-level2.s3.amazonaws.com/{}/{}/{}/{}/{}".format(year,day,hour,station,input)
    write_logs(fs)
    return {"url":fs}
















