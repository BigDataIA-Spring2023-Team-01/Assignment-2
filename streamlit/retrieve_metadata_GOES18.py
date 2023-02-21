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
    logStreamName = "GOES18",
    logEvents= [
        {
            'timestamp' : int(time.time() * 1e3),
            'message' : message,
        }
    ]   
)  


bucket = 'noaa-goes18'
prefix = 'ABI-L1b-RadC/'
write_logs(bucket)
write_logs(prefix)

# Connect to SQLite database
conn = sqlite3.connect("results/s3_goes.db")
cursor = conn.cursor()

# Create table to store file names
cursor.execute("CREATE TABLE IF NOT EXISTS folders (year text, day_of_year text,hour text)")
write_logs("Creating table")

def query_into_dataframe():
    df = pd.read_sql_query("SELECT * FROM folders", conn)
    print(df)


#level 0 = 2022, level 1 = 2023
def create_list(result,level):
    l = []
    for o in result.get('CommonPrefixes'):
        val = o.get("Prefix").split('/')
        l.append(val[level])
    write_logs(l)        
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

retrieve_metadata(bucket,prefix)
# Commit the changes to the database
conn.commit()
query_into_dataframe()

# Close the connection to the database
conn.close()
