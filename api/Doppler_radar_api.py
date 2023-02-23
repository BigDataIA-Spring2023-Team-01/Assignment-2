import sqlite3
from fastapi import FastAPI
import uvicorn
import pandas as pd
import numpy as np



app = FastAPI()



@app.get("/coordinatesdata")
async def get_data_of_coordinates():
    conn = sqlite3.connect('../data/ddl.dbo')
    cursor = conn.cursor()
    def convert_coordinates(coordinates):
    
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
    
    
    latarray=[]
    longarray=[]
    

    # Check if the table exists
    table_name = "coordinates"
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cursor.fetchone():
        print("Table Exists")
        query = "SELECT Coordinates FROM coordinates"
        cursor.execute(query)
        results = cursor.fetchall()
        
        for row in results:
            convert_coordinates(row[0])
        return{"latitude":latarray,"longitude":longarray}


    else:
        print(f"Table '{table_name}' does not exist")
        

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


        for row in rows:
            convert_coordinates(row[0])
        return{"latitude":latarray,"longitude":longarray}
        
    conn.close()




if __name__ == "__main__":
    uvicorn.run(app, host="10.0.0.17", port=8000)