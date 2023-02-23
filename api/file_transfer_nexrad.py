import boto3
from fastapi import FastAPI, HTTPException
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
import boto3
from fastapi import FastAPI

router_file_transfer_nexrad = APIRouter()
s3client = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

USER_BUCKET_NAME = 'team01'

clientlogs = boto3.client('logs',
                        region_name= 'us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )


def transfer_file_to_S3_nexrad(filename,final_url):
        bucket = 'noaa-nexrad-level2'
        parts = filename.split("_")
        station_code = parts[0][:4] 
        year = parts[0][4:8] 
        day_of_year = parts[0][8:10] 
        hour = parts[0][10:]
        final_url = "https://noaa-nexrad-level2.s3.amazonaws.com/index.html#{}/{}/{}/{}/".format(year,day_of_year,hour,station_code)        
        print(final_url)
        with open(filename, "wb") as data:
                data.write(requests.get(final_url).content)
                s3client.upload_file(filename, USER_BUCKET_NAME,filename )
                print("success")

def url_gen_nexrad(input):
    arr = input.split("_")[0]
    year, day, hour, station = arr[4:8], arr[8:10], arr[10:12], arr[0:4]
    fs = "https://noaa-nexrad-level2.s3.amazonaws.com/{}/{}/{}/{}/{}".format(year,day,hour,station,input)
    write_logs(fs)
    return fs


def check_file_exists(filename, bucket_name):
    try:
        s3client.head_object(Bucket=bucket_name, Key=filename)
        # print("here")
        return True
    except Exception as e:
        return False

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

@router_file_transfer_nexrad.get("/transfer_file_nexrad")
def transfer_file_nexrad(filename: str):
    file_to_transfer = url_gen_nexrad(filename)

    if check_file_exists(filename,USER_BUCKET_NAME):
       return {'S3-Personal':'https://{}.s3.amazonaws.com/{}'.format(USER_BUCKET_NAME,filename),
               'S3-Public':file_to_transfer}
    else:
        transfer_file_to_S3_nexrad(filename,file_to_transfer)

        return {'S3-Personal':'https://{}.s3.amazonaws.com/{}'.format(USER_BUCKET_NAME,filename),
               'S3-Public':file_to_transfer}
    

