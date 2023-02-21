import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import csv



latarray=[]
longarray=[]


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
    


# Connect to the database file
conn = sqlite3.connect("results/ddl.dbo")
cursor = conn.cursor()

# Check if the table exists
table_name = "coordinates"
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
if cursor.fetchone():
    print(f"Table '{table_name}' exists")
    cursor.execute("SELECT * FROM coordinates")
    rows = cursor.fetchall()
    
    
    for row in rows:
        convert_coordinates(row[4])
else:
    print(f"Table '{table_name}' does not exist")
    conn = sqlite3.connect("results/ddl.dbo")
    cursor = conn.cursor()

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
    df = pd.read_csv("results/Book.csv",encoding = 'unicode_escape')
    df.to_sql("coordinates", conn, if_exists="replace")
    # Commit changes and close the connection
    conn.commit()

    cursor.execute("SELECT Coordinates FROM coordinates")
    rows = cursor.fetchall()

    
    for row in rows:
        convert_coordinates(row[0])

conn.close()

df = pd.DataFrame({
    
    'lat' : latarray,
    'lon' : longarray
})
st.title("Points of all NEXRAD Doppler radars")
st.map(df)
