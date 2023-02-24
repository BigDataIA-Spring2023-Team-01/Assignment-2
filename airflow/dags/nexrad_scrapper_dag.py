from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
import os
import requests
import re
import sqlite3
import boto3
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from great_expectations.core.batch import BatchRequest
from great_expectations.data_context.types.base import (
    DataContextConfig,
    CheckpointConfig
)
 

#load env variables
dotenv_path = Path('./dags/.env')
load_dotenv(dotenv_path=dotenv_path)
#authenticate S3 client with your user credentials that are stored in your .env config file
s3client = boto3.client('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

dag = DAG(
    dag_id="nex_Scrapper",
    schedule="0 0 * * *",   #run daily - at midnight
    start_date=days_ago(0),
    catchup=False,
    tags=["damg7245", "assignments", "nexrad_scrapping"],
)

def scrape_nexrad_data():

    

    #intialise dictionary to store scraped data before moving it to a sqllite table
    scraped_nexrad_dict = {
        'id': [],
        'year': [],
        'month': [],
        'day': [],
        'ground_station': []
    }

    
    id=1    
    bucket = 'noaa-nexrad-level2'
    years_to_scrape = ['2022', '2023']      #considering only 2 years as per scope of assignment

    for year in years_to_scrape:
        prefix = year+"/"    #replace this with user input from streamlit UI with / in end
        result = s3client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')
        
        for o in result.get('CommonPrefixes'):
            path = o.get('Prefix').split('/')
            prefix_2 = prefix + path[-2] + "/"      
            sub_folder = s3client.list_objects(Bucket=bucket, Prefix=prefix_2, Delimiter='/')
            for p in sub_folder.get('CommonPrefixes'):
                sub_path = p.get('Prefix').split('/')
                prefix_3 = prefix_2 + sub_path[-2] + "/"    
                sub_sub_folder = s3client.list_objects(Bucket=bucket, Prefix=prefix_3, Delimiter='/')
                for q in sub_sub_folder.get('CommonPrefixes'):
                    sub_sub_path = q.get('Prefix').split('/')  
                    scraped_nexrad_dict['id'].append(id)   #map all scraped data into the dict
                    scraped_nexrad_dict['year'].append(sub_sub_path[0])
                    scraped_nexrad_dict['month'].append(sub_sub_path[1])
                    scraped_nexrad_dict['day'].append(sub_sub_path[2])
                    scraped_nexrad_dict['ground_station'].append(sub_sub_path[3])
                    id+=1

   
    scraped_nexrad_df = pd.DataFrame(scraped_nexrad_dict)     #final scraped metadata stored in dataframe
    #next, store this scraped data into a database; define variables for database name, individual sql scripts and individual table names
    database_file_name = 'scraped_df_nexrad_metadata.db'
    nexrad_ddl_file_name = 'sql_nexrad.sql'
    nexrad_table_name = 'NEXRAD_METADATA'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__),nexrad_ddl_file_name)
    #first check if the database file exists or not
    if not Path(database_file_path).is_file():  #if .db does not exist, create one
       
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        cursor.executescript(sql_script)    #execute the sql script to create the table
        scraped_nexrad_df.to_sql(nexrad_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists
    
    else:   
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        scraped_nexrad_df.to_sql(nexrad_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists

    db_conn.commit()
    db_conn.close()     
   
def export_db():
    s3res = boto3.resource('s3', region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))
    s3res.Bucket(os.environ.get('USER_BUCKET_NAME')).upload_file("./dags/scraped_df_nexrad_metadata.db", "database-files/scraped_df_nexrad_metadata.db")
   

    database_file_name = 'scraped_df_nexrad_metadata.db'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    conn = sqlite3.connect(database_file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    
    nexrad_df = pd.read_sql_query("SELECT * FROM NEXRAD_METADATA", conn)

    
    s3client.put_object(Body=nexrad_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='database-files/nexrad_data.csv')

with dag:

   
    get_nexrad_metadata = PythonOperator(
        task_id = 'scrape_nexrad_data',
        python_callable = scrape_nexrad_data,
        start_date=days_ago(0)
    )

    

    export_to_csv = PythonOperator(
        task_id = 'export_db',
        python_callable = export_db,
        start_date=days_ago(0)
    )
    
    get_nexrad_metadata >> export_to_csv

# # GE using airflow
# great_expectations_dag = DAG(
#     'GE_dag', 
#     #default_args=default_args, 
#     schedule_interval=timedelta(days=1)
#     )
# ge_root_dir=os.path.join(os.path.dirname(__file__),"..","great-expectation/great-expectation")
# GE_nexrad1st = GreatExpectationsOperator(
#     task_id="nexrad_run_data_validation",
#     data_context_root_dir=ge_root_dir,
#     checkpoint_name="nexrad_checkpoint.yml",
#     dag=great_expectations_dag
# )

# GE_nexrad2nd = GreatExpectationsOperator(
#     task_id="great_expectations_config",
#     data_context_config="great_expectations.yml",
#     checkpoint_config="nexrad_checkpoint.yml",
#     dag=great_expectations_dag
# )
# GE_nexrad1st >>  GE_nexrad2nd

