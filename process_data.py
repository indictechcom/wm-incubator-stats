import json
import os
from datetime import datetime

import pandas as pd
import urllib.request
import toolforge as forge

user_agent = forge.set_user_agent(
    tool='Wikimedia Incubator Dashboard',
    url='https://incubatordashboard.toolforge.org/',
    email='kcvelaga@gmail.com'
)

project_labels = {
    "Wp": "Wikipedia",
    "Wt": "Wiktionary",
    "Wq": "Wikiquote",
    "Wb": "Wikibooks",
    "Wy": "Wikivoyage",
    "Wn": "Wikinews",
}

column_labels = {
    "project": "Project"
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

conn = forge.connect('incubatorwiki')
with conn.cursor() as cur:
    cur.execute(query)
    result = cur.fetchall()

stats = pd.DataFrame(result, columns=column_labels.values().tolist())
stats['Project'] = stats['Project'].apply(lambda x: x.decode('utf-8'))
print(type(stats))
print(stats.columns)
print(stats)

stats_path = "stats"
with open(f"{stats_path}/dates.json", "r") as file:
    dated_files = json.load(file)

dated_files_sorted = sorted(
    dated_files.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")
)
latest_dt, latest_file = dated_files_sorted[-1]

df = pd.read_csv(f"{stats_path}/raw/{latest_file}", sep="\t")

project_cols = ["Project", "Language Code"]
df[project_cols] = df["prefix"].str.split("/", expand=True)

df = df.rename(column_labels, axis=1)
df["Project"] = df["Project"].map(project_labels)

select_cols = project_cols + list(column_labels.values())
df = df[select_cols]
df.to_csv(f"stats/processed/{latest_file}", sep="\t", index=False)
