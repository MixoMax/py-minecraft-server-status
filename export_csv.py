import sqlite3
from fastapi import FastAPI
import uvicorn
import pandas as pd
import os

app = FastAPI()

@app.get("/export")
async def export():
    # copy database file
    os.system("cp stats.db stats_copy.db")
    # connect to database
    db = sqlite3.connect("stats_copy.db")
    # read data from database
    data = pd.read_sql_query("SELECT * FROM stats", db)
    
    # export data to csv
    data.to_csv("stats.csv", index=False)

    return_str = ""
    with open("stats.csv", "r") as f:
        return_str = f.read()
    
    return return_str