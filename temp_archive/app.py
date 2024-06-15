from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
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

def create_figure(data, param, slider_values):
    filtered_data = data[(data[param] >= slider_values[0]) & (data[param] <= slider_values[1])]
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(filtered_data.columns), align='left', fill_color='paleturquoise', font=dict(size=14)),
        cells=dict(values=[filtered_data[col] for col in filtered_data.columns], align='left', height=27.5, fill_color='mintcream', font=dict(size=14)))
    ])
    fig.update_layout(height=1000)
    return fig

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    latest_file_path = get_latest_data_file('stats/')
    main_df = pd.read_csv(latest_file_path, sep='\t')
    params = main_df.columns.tolist()[2:]  # Skip the first two columns which are non-numeric (likely project name, etc.)

    # Default values
    selected_wikis = list(main_df.Project.unique())
    selected_param = params[0]  # Default to the first parameter for initial load
    slider_min = int(main_df[selected_param].min())
    slider_max = int(main_df[selected_param].max())
    slider_values = [slider_min, slider_max]
    latest_update = latest_file_path.split('/')[-1].split('.')[0]

    if request.method == 'POST':
        selected_wikis = request.form['hidden_tags'].split(',')
        selected_param = request.form['param']
        slider_values = [int(request.form['slider_min']), int(request.form['slider_max'])]

        # Update the slider range dynamically based on the selected parameter
        slider_min = int(main_df[selected_param].min())
        slider_max = int(main_df[selected_param].max())

    filtered_df = main_df[main_df.Project.isin(selected_wikis)]
    figure = create_figure(filtered_df, selected_param, slider_values)

    graph_html = figure.to_html(full_html=False)

    return render_template('dashboard.html',
                           wikis=list(main_df.Project.unique()),
                           params=params,
                           selected_wikis=selected_wikis,
                           selected_param=selected_param,
                           slider_min=slider_min,
                           slider_max=slider_max,
                           slider_values=slider_values,
                           graph_html=graph_html,
                           latest_update=str(latest_update))

if __name__ == '__main__':
    app.run(debug=True)
