import json
import os
from datetime import datetime, date

import pandas as pd
import urllib.request
import toolforge as forge

user_agent = forge.set_user_agent(
    tool='Wikimedia Incubator Dashboard',
    url='https://incubatordashboard.toolforge.org/',
    email='kcvelaga@gmail.com'
)

with open('stats/logs.json', 'r') as file:
    logs = json.load(file)

project_labels = {
    "Wp": "Wikipedia",
    "Wt": "Wiktionary",
    "Wq": "Wikiquote",
    "Wb": "Wikibooks",
    "Wy": "Wikivoyage",
    "Wn": "Wikinews",
}

column_labels = {
    "prefix": "Prefix",
    "edit_count": "Total edits",
    "actor_count": "Total editors",
    "pages_count": "Total pages",
    "bytes_removed_30D": "Bytes removed (last 30 days)",
    "bytes_added_30D": "Bytes added (last 30 days)",
    "avg_edits_3M": "Average monthly edits",
    "avg_editors_3M": "Average monthly editors",
}

sql_query_url = "https://raw.githubusercontent.com/indictechcom/wm-incubator-stats/main/query.sql"
with urllib.request.urlopen(sql_query_url) as response:
    query = response.read().decode()

curr_dt = date.today()
curr_dt_str = str(curr_dt)
curr_log = {}

try:
    conn = forge.connect('incubatorwiki')
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchall()

    stats = pd.DataFrame(result, columns=list(column_labels.keys()))
    stats['prefix'] = stats['prefix'].apply(lambda x: x.decode('utf-8'))
    curr_log['is_fetch_successful'] = True
except Exception as e:
    curr_log['is_fetch_successful'] = False
    curr_log['fetch_failure_reason'] = str(e)

if curr_log['is_fetch_successful']:
    try:
        project_cols = ["Project", "Language Code"]
        stats[project_cols] = stats["prefix"].str.split("/", expand=True)

        stats = stats.rename(column_labels, axis=1)
        stats["Project"] = stats["Project"].map(project_labels)

        select_cols = project_cols + list(column_labels.values())
        stats = stats[select_cols]
        print(stats.head(10))
        print(f"stats/{curr_dt_str}.tsv")

        stats.to_csv(f"stats/{curr_dt_str}.tsv", sep="\t", index=False)

        curr_log['is_processing_successful'] = True
    except Exception as e:
        curr_log['is_processing_successful'] = False
        curr_log['processing_failure_reason'] = str(e)

logs[curr_dt_str] = curr_log
with open('stats/logs.json', 'w') as outfile:
    json.dump(logs, outfile)
print(curr_log)
print(logs)