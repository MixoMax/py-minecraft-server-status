import requests
import re
import sqlite3
import time

from enum import Enum


host = "fsr-informatik.de"

db = sqlite3.connect("stats.db")
cursor = db.cursor()

cmd = """CREATE TABLE IF NOT EXISTS stats 
(time INTEGER PRIMARY KEY,
num_players INTEGER,
max_players INTEGER,
players TEXT)"""
cursor.execute(cmd)
db.commit()



def get_stats(host: str) -> tuple[int, int, list[str]]:
    res = requests.get(f"https://mcsrvstat.us/server/{host}")

    if res.status_code != 200:
        print(f"Error: {res.status_code}")
        return -res.status_code, -res.status_code, []
    
    html = res.text
    og_html = html

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
            max_players = int(match.group(2))

    
    players = []
    q_str = '<a href="https://namemc.com/profile/'
    end_str = "</a>"

    html = og_html

    while q_str in html:
        html = html[html.find(q_str) + len(q_str):]

        uuid_end = '"'
        uuid = html[:html.find(uuid_end)]
        html = html[html.find(uuid_end):]

        name_start = 'title="'
        name_end = '" />'

        name = html[html.find(name_start) + len(name_start):html.find(name_end)]
        html = html[html.find(name_end):]

        players.append(name)
    
    return num_players, max_players, players




    




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
        num_players, max_players, players = get_stats(host)
        
        players_str = ",".join(players)

        print(f"{current_time}: {num_players}/{max_players} players: {players_str}")
        cursor.execute("INSERT INTO stats VALUES (?, ?, ?, ?)", (current_time, num_players, max_players, players_str))
        db.commit()
