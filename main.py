import requests
import re
import sqlite3
import time

from enum import Enum


host = "fsr-informatik.de"

db = sqlite3.connect("stats.db")
cursor = db.cursor()

cmd = "CREATE TABLE IF NOT EXISTS stats (time INTEGER, num_players INTEGER, max_players INTEGER)"
cursor.execute(cmd)
db.commit()



def get_stats(host: str) -> tuple[int, int]:
    res = requests.get(f"https://mcsrvstat.us/server/{host}")

    if res.status_code != 200:
        print(f"Error: {res.status_code}")
        return -res.status_code, -res.status_code
    


    html = res.text

    # search for all <div class="col-md-10 mb-3">
    q_results = []
    q_str = '<div class="col-md-10 mb-3">'
    while q_str in html:
        q_results.append(html[html.find(q_str) + len(q_str):html.find("</div>", html.find(q_str))])
        html = html[html.find("</div>", html.find(q_str)):]


    num_players = -1
    max_players = -1

    regex = re.compile(r"(\d+) / (\d+)")
    for q in q_results:
        match = regex.search(q)
        if match:
            num_players = int(match.group(1))
            print(match.group(1))
            max_players = int(match.group(2))

    return num_players, max_players


print("Linus Horn´s Minecraft Server Status logger")
print("Host: ", host)
print("Interval: 5s")
print("error codes: -1: no connection (server is probably offline), -X: HTTP error code X")


interval = 5
last_query = 0
while True:
    current_time = int(time.time())
    if current_time - last_query >= interval:
        last_query = current_time
        num_players, max_players = get_stats(host)
        print(f"Num players: {num_players}, Max players: {max_players}")
        cursor.execute("INSERT INTO stats (time, num_players, max_players) VALUES (?, ?, ?)", (current_time, num_players, max_players))
        db.commit()