from datetime import datetime as dt
import pandas as pd
import os
import mysql.connector

dbname = os.environ.get('DB_NAME')
dbuser = os.environ.get('DB_USER')
dbpassword = os.environ.get('DB_PASSWORD')
dbhost = os.environ.get('DB_HOST')
dbport = os.environ.get('DB_PORT')

conn = mysql.connector.connect(dbname=dbname, user=dbuser, password=dbpassword, host=dbhost, port=dbport)
cur = conn.cursor()

project_labels = {
        'Wp': 'Wikipedia',
        'Wt': 'Wiktionary',
        'Wq': 'Wikiquote',
        'Wb': 'Wikibooks',
        'Wy': 'Wikivoyage',
        'Wn': 'Wikinews'
    }

column_labels = {
        'edit_count': 'Edits (all time)',
        'actor_count': 'Editors (all time)',
        'pages_count': 'Pages (all time)',
        'bytes_removed_30D': 'Bytes removed (previous month)',
        'bytes_added_30D':  'Bytes added (previous month)',
        'avg_edits_3M': 'Average Edits per Month',
        'avg_editors_3M': 'Average Editors per Month'}


with open('query.sql', 'r') as f:
    sql = f.read()
cur.execute(sql)
rows = cur.fetchall()
column_headers = (desc[0] for desc in cur.description)

stats_path = 'stats/'
curr_time = dt.now()
curr_file_path = f'{stats_path}{curr_time}.tsv'
df = pd.DataFrame(rows , columns=column_headers)
df[['Project', 'Language Code']] = df.iloc[:,0].str.split('/', expand=True)
df.drop(df.columns[0], axis=1, inplace=True)    
df.rename(column_labels,axis=1, inplace=True)
df['Project'] = df['Project'].map(project_labels)

df = df[['Project', 'Language Code', 
        'Average Edits per Month', 'Average Editors per Month', 
        'Edits (all time)', 'Editors (all time)', 
        'Pages (all time)', 'Bytes added (previous month)',
        'Bytes removed (previous month)']]

df.to_csv(curr_file_path, sep='\t', index=False)