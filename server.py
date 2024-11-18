from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.requests import Request
import uvicorn

import sqlite3
import re
from datetime import datetime


app = FastAPI()


db = sqlite3.connect("stats.db")
cursor = db.cursor()

cmd = """CREATE TABLE IF NOT EXISTS stats 
(time INTEGER PRIMARY KEY UNIQUE,
num_players INTEGER,
max_players INTEGER,
players TEXT)"""
cursor.execute(cmd)
db.commit()


YYYY_MM_DD_HH_MM = re.compile(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})")


@app.get("/")
async def root():
    return FileResponse("index.html")


@app.post("/api/v1/log_stats")
async def log_stats(request: Request):
    data = await request.json()
    timestamp = data.get("timestamp")
    players = data.get("players")
    max_players = data.get("max_players")
    # timestamp: UNIX timestamp from int(time.time())

    print(f"{timestamp=}, {players=}, {max_players=}")

    cursor.execute("INSERT INTO stats VALUES (?, ?, ?, ?)", (timestamp, len(players), max_players, ",".join(players)))
    db.commit()
    return JSONResponse(content={"status": "ok"})

@app.get("/api/v1/get_stats")
async def get_stats(t_start: str, t_end: str):
    if not (YYYY_MM_DD_HH_MM.match(t_start) and YYYY_MM_DD_HH_MM.match(t_end)):
        return JSONResponse(content={"status": "error", "message": "Invalid timestamp format! Use YYYY-MM-DD HH:MM"}, status_code=400)
    
    # Convert timestamps to UNIX timestamps
    t_start = int(datetime.strptime(t_start, "%Y-%m-%d %H:%M").timestamp())
    t_end = int(datetime.strptime(t_end, "%Y-%m-%d %H:%M").timestamp())

    cursor.execute("SELECT * FROM stats WHERE time >= ? AND time <= ? AND num_players > 0", (t_start, t_end))
    rows = cursor.fetchall()

    min_timestamp = 1e18
    max_timestamp = -1
    min_n_players = 1e6
    max_n_players = -1

    for row in rows:
        min_timestamp = min(min_timestamp, row[0])
        max_timestamp = max(max_timestamp, row[0])
        min_n_players = min(min_n_players, row[1])
        max_n_players = max(max_n_players, row[1])
    
    return JSONResponse(content={
        "status": "ok",
        "min_timestamp": min_timestamp,
        "max_timestamp": max_timestamp,
        "min_n_players": min_n_players,
        "max_n_players": max_n_players,
        "data": rows
    }, status_code=200)

@app.get("/api/v1/current_stats")
async def current_stats():
    cursor.execute("SELECT * FROM stats ORDER BY time DESC LIMIT 1")
    row = cursor.fetchone()
    return JSONResponse(content={
        "status": "ok" if row[2] > 0 else "error",
        "timestamp": row[0],
        "timestamp_human": datetime.fromtimestamp(row[0]).strftime("%Y-%m-%d %H:%M:%S"),
        "num_players": row[1],
        "max_players": row[2],
        "players": row[3].split(",")
    }, status_code=200)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)