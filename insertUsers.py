import sqlite3
import pandas as pd
import requests
import os
db_path = 'data/login.dbo'
sql_path = 'sql/db_users.sql'
scriptdir = os.path.dirname(__file__)
db_path = os.path.join(scriptdir, db_path)
sql_path = os.path.join(scriptdir, sql_path)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
with open(sql_path, 'r') as f:
    script = f.read()
cursor.executescript(script)

conn.commit()
conn.close()
