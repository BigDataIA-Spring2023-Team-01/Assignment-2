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

class Geos_metadata(BaseModel):
    url: str | None = None
    prefix: str | None = None

#---------------------------------------------------------------------------------------------------------------
#                            Connection Declarations
#---------------------------------------------------------------------------------------------------------------
#

router_metadata_geos = APIRouter()
load_dotenv()
s3 = boto3.client('s3',region_name='us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

clientlogs = boto3.client('logs',
                            region_name= 'us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                            )
conn = sqlite3.connect("data/s3_goes.dbo")
cursor = conn.cursor()
#---------------------------------------------------------------------------------------------------------------
#                            Function Declarations
#---------------------------------------------------------------------------------------------------------------
#
def write_logs(message: str):
        clientlogs.put_log_events(
        logGroupName =  "Assignment_1",
        logStreamName = "GOES18",
        logEvents= [
            {
                'timestamp' : int(time.time() * 1e3),
                'message' : message,
            }
        ]   
    )  
        
def query_into_dataframe():
        df = pd.read_sql_query("SELECT * FROM folders", conn)
        print(df)


    #level 0 = 2022, level 1 = 2023
def create_list(result,level):
    l = []
    for o in result.get('CommonPrefixes'):
        val = o.get("Prefix").split('/')
        l.append(val[level])
    write_logs(str(l))        
    return l

def retrieve_metadata(bucket,prefix):
    year,day_of_year,hour = [],[],[]
    result = s3.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')
    year = create_list(result,1)

    for i in year:
        tprefix = prefix + str(i) + "/"
        result_1 = s3.list_objects(Bucket=bucket, Prefix=tprefix, Delimiter='/')
        doy = create_list(result_1,2)
        day_of_year.append(doy)

        for j in doy:
            ttprefix = tprefix + str(j) + "/"
            result_2 = s3.list_objects(Bucket=bucket, Prefix=ttprefix, Delimiter='/')
            h = create_list(result_2,3)
            hour.append(h)

    populate_db(year,day_of_year,hour)

def populate_db(year, day_of_year,hour):
    i = 0
    for y in year:
        day_of_year_aaray = day_of_year[i]
        j = 0
        for d in day_of_year_aaray:
            hour_array = hour[j]
            for h in hour_array:
                #print("year:",type(y),"day:",type(d),"Hour:",type(h))
                cursor.execute("INSERT INTO folders VALUES(?,?,?)",(y,d,h))
            j+=1
        i+=1
    write_logs("Db_populated")

        
#---------------------------------------------------------------------------------------------------------------
#                            API Declarations
#---------------------------------------------------------------------------------------------------------------
#



@router_metadata_geos.get("/retrieve_metadata/geos", response_model=Token)
async def retrieve_metadata_geos():
    
    bucket = 'noaa-goes18'
    prefix = 'ABI-L1b-RadC/'
    # write_logs(bucket)
    # write_logs(prefix)

    # Create table to store file names
    cursor.execute("CREATE TABLE IF NOT EXISTS folders (year text, day_of_year text,hour text)")
    # write_logs("Creating table")


    retrieve_metadata(bucket,prefix)
    # Commit the changes to the database
    conn.commit()

    # Close the connection to the database
    conn.close()
    return {"db_file_name":"s3_goes.dbo",
            "db_file_location":"/home/chromite/projects/Assignment-2/data/s3_goes.dbo"}
    
