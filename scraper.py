import requests
import re
import time

from datetime import datetime


host = "31.16.124.24"





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


def upload_stats(host: str):
    num_players, max_players, players = get_stats(host)
    timestamp = int(time.time())

    print(f"{datetime.fromtimestamp(timestamp)}: {num_players}/{max_players} players")

    res = requests.post("http://localhost:8002/api/v1/log_stats", json={"timestamp": timestamp, "players": players, "max_players": max_players})

    if res.status_code != 200:
        print(f"Error: {res.status_code}")
        print(res.json())
        return -res.status_code

    return 0


interval = 5 #s

while True:
    t_start = time.time()

    upload_stats(host)

    t_end = time.time()

    time.sleep(max(0, interval - (t_end - t_start)))
