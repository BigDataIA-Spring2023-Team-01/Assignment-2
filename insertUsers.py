import sqlite3
import pandas as pd
import requests


conn = sqlite3.connect("/home/chromite/projects/Assignment-2/data/login.dbo")
cursor = conn.cursor()
with open('/home/chromite/projects/Assignment-2/sql/db_users.sql', 'r') as f:
    script = f.read()
cursor.executescript(script)

conn.commit()
conn.close()
