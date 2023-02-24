import sqlite3
from fastapi import FastAPI,APIRouter
import uvicorn
import pandas as pd
import numpy as np
import jwt


router_nexrad_coords = APIRouter()

def convert_coordinates(coordinates):
        
        latarray=[]
        longarray=[]
        individual_coordinates = coordinates.split(" ")
        latitude = individual_coordinates[0]
        longitude = individual_coordinates[1]

        if 'N' in latitude:
            latitude = latitude[:-2]
        else:
            latitude = '-' + latitude[:-1]

        if 'W' in longitude:
            longitude = '-' + longitude[:-2]
        else:
            longitude = longitude[:-2]
        latarray.append(float(latitude))
        longarray.append(float(longitude))

        return [latarray, longarray]

@router_nexrad_coords.get("/coordinatesdata")
async def get_data_of_coordinates(current_user: jwt.User = jwt.Depends(jwt.get_current_active_user)):
    conn = sqlite3.connect("../data/ddl.dbo")
    cursor = conn.cursor()
    
    latarray=[]
    longarray=[]
    


    # Check if the table exists
    table_name = "coordinates"
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cursor.fetchone():
        final_arr_lat,final_arr_long = [],[]
        print("Table Exists")
        query = "SELECT Coordinates FROM coordinates"
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            r= convert_coordinates(row[0])
            final_arr_lat.append(r[0][0])
            final_arr_long.append(r[1][0])

        
        return{"latitude":final_arr_lat,"longitude":final_arr_long}


    else:
        print(f"Table '{table_name}' does not exist")
        final_arr = []


        # Create the table
        cursor.execute("""
        CREATE TABLE coordinates (
            state text,
            place text,
            ICAO_Location_Identifier text,
            Coordinates text
        )
        """)

        # Load data from CSV into the table
        df = pd.read_csv("../data/Book1.csv",encoding = 'unicode_escape')
        df.to_sql("coordinates", conn, if_exists="replace")
        # Commit changes and close the connection
        conn.commit()

        cursor.execute("SELECT Coordinates FROM coordinates")
        rows = cursor.fetchall()


        for row in results:
            r= convert_coordinates(row[0])
            final_arr_lat.append(r[0])
            final_arr_long.append(r[1])
        print(final_arr_lat,final_arr_lat)
        return{"latitude":final_arr_lat,"longitude":final_arr_lat}

        
    conn.close()

