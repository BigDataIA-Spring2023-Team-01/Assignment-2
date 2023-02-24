from datetime import datetime, timedelta
from exceptiongroup import catch
from fastapi import Depends, FastAPI, HTTPException, status,Form,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import sqlite3
from sqlite_utils import Database
import json
import os
import logging
from dotenv import load_dotenv
import boto3
import time
import pandas as pd
import api.jwt
jwt = api.jwt
#---------------------------------------------------------------------------------------------------------------
#                            Class Declarations
#---------------------------------------------------------------------------------------------------------------
#
class Token(BaseModel):
    db_file_name:str
    db_file_location:str

class Nexrad_metadata(BaseModel):
    url: str | None = None
    prefix: str | None = None

#---------------------------------------------------------------------------------------------------------------
#                            Connection Declarations
#---------------------------------------------------------------------------------------------------------------
#

router_metadata_nexrad = APIRouter()
load_dotenv()
s3 = boto3.client('s3',region_name='us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

clientlogs = boto3.client('logs',
                            region_name= 'us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                            )
conn = sqlite3.connect("data/s3_nexrad.dbo")
cursor = conn.cursor()




#---------------------------------------------------------------------------------------------------------------
#                            Function Declarations
#---------------------------------------------------------------------------------------------------------------
#
def write_logs(message: str):
    clientlogs.put_log_events(
    logGroupName =  "Assignment_1",
    logStreamName = "nexrad",
    logEvents= [
        {
            'timestamp' : int(time.time() * 1e3),
            'message' : message,
        }
    ]   
)  

        
def create_list(result,level):
    l = []
    for o in result.get('CommonPrefixes'):
        val = o.get("Prefix").split('/')
        l.append(val[level])

    return l

def retrieve_metadata_NEXRAD(bucket):
    year,month,day,nexrad_station = ['2022','2023'],[],[],[]
    for i in range(len(year)):
        prefix = str(year[i]) + "/"
        result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter='/')
        month = create_list(result,1)
        print(month)
        for j in range(len(month)):
            tprefix = prefix + str(month[j]) + "/"
            result = s3.list_objects_v2(Bucket=bucket, Prefix=tprefix, Delimiter='/')
            day = create_list(result,2)
            print(day)
            for n in range(len(day)):
                ttprefix = tprefix + str(day[n]) + "/"
                result = s3.list_objects_v2(Bucket=bucket, Prefix=ttprefix, Delimiter='/')
                nexrad_station = create_list(result,3)
                populate_db(year[i],month[j],day[n],nexrad_station)

def populate_db(year,month, day,nexrad_station):
    cursor.execute("INSERT INTO folders VALUES(?,?,?,?)",(year,month,day,str(nexrad_station)))

#---------------------------------------------------------------------------------------------------------------
#                            API Declarations
#---------------------------------------------------------------------------------------------------------------
#



@router_metadata_nexrad.get("/retrieve_metadata/nexrad", response_model=Token)
async def retrieve_metadata_nexrad():
    
    cursor.execute("CREATE TABLE IF NOT EXISTS folders (year text, month text, day text,nexrad_station text)")
    bucket = 'noaa-nexrad-level2'
    write_logs(bucket)



    # Create table to store file names
    cursor.execute("CREATE TABLE IF NOT EXISTS folders (year text, day_of_year text,hour text)")
    # write_logs("Creating table")


    retrieve_metadata_NEXRAD(bucket)
    # Commit the changes to the database
    conn.commit()

    # Close the connection to the database
    conn.close()
    return {"db_file_name":"s3_nexrad.dbo",
            "db_file_location":"/home/chromite/projects/Assignment-2/data/s3_nexrad.db"}
    
