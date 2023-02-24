# Assignment-2

[![fastapi-ci](https://github.com/BigDataIA-Spring2023-Team-01/Assignment-2/actions/workflows/fastapi.yml/badge.svg)](https://github.com/BigDataIA-Spring2023-Team-01/Assignment-2/actions/workflows/fastapi.yml)


Reference:

## api folder /api
This folder contains all the api method functions and their respective functional dependencies. They are named as per the functionality - for example: api/metadata_geos.py - contains the api methods for extracting metadata from the Public aws geos bucket to a database.

## data folder /data
This contains all the database file and csv files.

## sql folder /sql
This folder contains all the sql scripts that are being used in this application.

## streamlit /streamlit
This contains all the streamlit pages and use the api calls from /api folder to do any task.

# How to Run
1. Open terminal
2. Browse the location where you want to clone the repository
3. Write the following command and press enter 
````
  git clone https://github.com/BigDataIA-Spring2023-Team-01/Assignment-2.git
 ````
 4. Create a virtual environment using the following command
 ````
  python -m venv <Virtual_environment_name>
 ````
 5. Activate the virtual environment and download the requirements.txt using
 ````
  pip install -r /path/to/requirements.txt
 ````
6. User docker compose to run both FastAPI and Streamlit containers.
 ````
  docker compose up -d --build
 ````
 
 ## Declaration 
 Contribution 
 
 1. Anandita Deb : 25%
 2. Cheril Yogi :25%
 3. Shamin Chokshi :25%
 4. Thejas Bharadwaj :25%
 
 WE ATTEST THAT WE HAVEN'T USED ANY OTHER STUDENT'S WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.
