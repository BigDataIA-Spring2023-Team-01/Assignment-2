import sqlite3
import boto3
import os
import logging
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()
s3 = boto3.client('s3',region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

clientlogs = boto3.client('logs',
                        region_name= 'us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

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

conn = sqlite3.connect("results/s3_nexrad.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS folders (year text, month text, day text,nexrad_station text)")
bucket = 'noaa-nexrad-level2'
write_logs(bucket)



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
                print(nexrad_station)
                populate_db(year[i],month[j],day[n],nexrad_station)

def populate_db(year,month, day,nexrad_station):
    cursor.execute("INSERT INTO folders VALUES(?,?,?,?)",(year,month,day,str(nexrad_station)))


retrieve_metadata_NEXRAD(bucket)
# Commit the changes to the database
# cursor.execute('''update table folders set nexrad_station = 'DOP1' where day = '01' and "month" = '02' and Is2023 = '1' ''' )

conn.commit()


# Close the connection to the database
conn.close()
