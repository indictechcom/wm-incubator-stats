import pandas as pd
from datetime import datetime as dt

project_labels = {
    'Wp': 'Wikipedia',
    'Wt': 'Wiktionary',
    'Wq': 'Wikiquote',
    'Wb': 'Wikibooks',
    'Wy': 'Wikivoyage',
    'Wn': 'Wikinews'}

stats_path = 'stats/'
curr_time = dt.now()
#curr_file_path = f'{stats_path}{curr_time.strftime("%B").lower()}_{str(curr_time.year)}.tsv'
curr_file_path = f'{stats_path}{curr_time.strftime("%B").lower()}_{str(curr_time.year-1)}.tsv'
df = pd.read_csv(curr_file_path, sep='\t')

df['Project'] = df.prefix.apply(lambda x:project_labels[x.split('/')[0]])
df['Language Code'] = df.prefix.apply(lambda x:x.split('/')[1])
df.drop('prefix', axis=1, inplace=True)

column_labels = {
    'edit_count': 'Edits (all time)',
    'actor_count': 'Editors (all time)',
    'pages_count': 'Pages (all time)',
    'bytes_removed_30D': 'Bytes removed (previous month)',
    'bytes_added_30D':  'Bytes added (previous month)',
    'avg_edits_3M': 'Average Edits per Month',
    'avg_editors_3M': 'Average Editors per Month'}

df.rename(column_labels, axis=1, inplace=True)

df = df[['Project', 'Language Code', 
         'Average Edits per Month', 'Average Editors per Month', 
         'Edits (all time)', 'Editors (all time)', 
         'Pages (all time)', 'Bytes added (previous month)',
         'Bytes removed (previous month)']]

df.to_csv(curr_file_path, sep='\t', index=False)


