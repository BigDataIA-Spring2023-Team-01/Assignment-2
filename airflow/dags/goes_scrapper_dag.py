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
    dag_id="Scrapper_goes18",
    schedule="0 0 * * *",   #run daily - at midnight
    start_date=days_ago(0),
    catchup=False,
    tags=["damg7245", "assignments", "goes_scrapping"],
)

def scrape_goes18_data():

   
    #intialise dictionary to store scraped data before moving it to a sqllite table
    scraped_goes18_dict = {
        'id': [],
        'product': [],
        'year': [],
        'day': [],
        'hour': []
    }

    id=1    
    bucket = 'noaa-goes18'
    prefix = "ABI-L1b-RadC/"    #just one product to consider as per scope of assignment
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
                sub_sub_path = sub_sub_path[:-1]   
                scraped_goes18_dict['id'].append(id)   #map all scraped data into the dict
                scraped_goes18_dict['product'].append(sub_sub_path[0])
                scraped_goes18_dict['year'].append(sub_sub_path[1])
                scraped_goes18_dict['day'].append(sub_sub_path[2])
                scraped_goes18_dict['hour'].append(sub_sub_path[3])
                id+=1

   
      
    scraped_goes18_df = pd.DataFrame(scraped_goes18_dict)     #final scraped metadata stored in dataframe

    #next, store this scraped data into a database; define variables for database name, individual sql scripts and individual table names
    database_file_name = 'scraped_db.db'
    goes_ddl_file_name = 'sql_goes18.sql'
    goes_table_name = 'GOES_METADATA'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__),goes_ddl_file_name)
    #first check if the database file exists or not
    if not Path(database_file_path).is_file():  #if .db does not exist, create one
        
        #create database
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        scraped_goes18_df.to_sql(goes_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists
    
    else:   #if database already exists
        
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        scraped_goes18_df.to_sql(goes_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists

    db_conn.commit()
    db_conn.close()     #finally commit changes to database and close
    

def export_db():
    s3res = boto3.resource('s3', region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))
    s3res.Bucket(os.environ.get('USER_BUCKET_NAME')).upload_file("./dags/scraped_db.db", "database-files/scraped_db.db")
   

    database_file_name = 'scraped_db.db'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    conn = sqlite3.connect(database_file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    goes_df = pd.read_sql_query("SELECT * FROM GOES_METADATA", conn)
    

    s3client.put_object(Body=goes_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='database-files/goes18_data.csv')
    

with dag:

    get_goes18_metadata = PythonOperator(
        task_id = 'scrape_goes18_data',
        python_callable = scrape_goes18_data,
        start_date=days_ago(0)

    )

   
    export_to_csv = PythonOperator(
        task_id = 'export_db',
        python_callable = export_db,
        start_date=days_ago(0)

    )
    
    get_goes18_metadata >> export_to_csv

# ## GREAT EXPECTATIONS USING AIRFLOW -

# great_expectations_dag = DAG(
#     'GE_dag', 
#     #default_args=default_args, 
#     schedule_interval=timedelta(days=1),
#     start_date=days_ago(0),
#     catchup = False

#     )
# ge_root_dir=os.path.join(os.path.dirname(__file__),"..","great-expectation/expectations")
# GE_goes1st = GreatExpectationsOperator(
#     task_id="goes18_run_data_validation",
#     data_context_root_dir=ge_root_dir,
#     checkpoint_name="goes18_check_point.yml",
#     dag=great_expectations_dag,
#     start_date=days_ago(0)


# )

# GE_goes2nd = GreatExpectationsOperator(
#     task_id="great_expectations_config",
#     data_context_config="great_expectations.yml",
#     checkpoint_config="goes18_check_point.yml",
#     dag=great_expectations_dag,
#     dag=great_expectations_dag

# )

# GE_goes1st >> GE_goes2nd 

