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
import jwt

router_file_transfer = APIRouter()
s3client = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

USER_BUCKET_NAME = 'team01'

clientlogs = boto3.client('logs',
                        region_name= 'us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )


def transfer_file_to_S3(selected_file,final_url):
        bucket = 'noaa-goes18'
        arr = selected_file.split("_")
        date = arr[3]
        year, day_of_year, hour = date[1:5], date[5:8], date[8:10]
        final_url = "https://noaa-goes18.s3.amazonaws.com/index.html#ABI-L1b-RadC/{}/{}/{}/{}".format(year,day_of_year,hour,selected_file)
        print(final_url)
        with open(selected_file, "wb") as data:
                data.write(requests.get(final_url).content)
                s3client.upload_file(selected_file, USER_BUCKET_NAME,selected_file )
                print("success")


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

@router_file_transfer.get("/transfer_file")
def transfer_file(filename: str,current_user: jwt.User = jwt.Depends(jwt.get_current_active_user)):
    file_to_transfer = url_gen_goes(filename)

    if check_file_exists(filename,USER_BUCKET_NAME):
       return {'S3-Personal':'https://{}.s3.amazonaws.com/{}'.format(USER_BUCKET_NAME,filename),
               'S3-Public':file_to_transfer}
    else:
        transfer_file_to_S3(filename,file_to_transfer)

        return {'S3-Personal':'https://{}.s3.amazonaws.com/{}'.format(USER_BUCKET_NAME,filename),
               'S3-Public':file_to_transfer}
    
