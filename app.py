from flask import Flask
from datetime import datetime
import pandas as pd
import glob
import os

app = Flask(__name__)

def get_latest_data_file(stats_path):
    data_files = glob.glob(os.path.join(stats_path, "*.tsv"))

    if not data_files:
        return None

    def extract_date(filename):
        date_str = filename.split('/')[-1].split('.')[0]
        return date_str

    data_files.sort(key=extract_date, reverse=True)
    return data_files[0]


@app.route('/fetch/', methods = ['GET'])
def fetch():
    stats_path = 'stats/'
    latest_file_path = get_latest_data_file(stats_path)
    main_df = pd.read_csv(latest_file_path, sep='\t')
    wikis_list = list(main_df['Project'].unique())
    params = main_df.columns.tolist()[2:]
    min = str(main_df[params[0]].min())
    max = str(main_df[params[0]].max())
    last_updated = os.path.basename(latest_file_path).split('.')[0]
    overview_data = main_df.to_dict('records')
    return {
        "wikis_list" : wikis_list,
        "params" : params,
        "min":min,
        "max":max,
        "overview_data":overview_data,
        "last_updated":last_updated
    }

app.run(port=3000)