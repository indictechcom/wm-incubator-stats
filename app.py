from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

app = Flask(__name__)

stats_path = '../wm-incubator-stats/stats/'
curr_time = datetime.now()
curr_file_path = f'{stats_path}{curr_time.strftime("%B").lower()}_{str(curr_time.year-1)}.tsv'
main_df = pd.read_csv(curr_file_path, sep='\t')


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
    selected_wikis = list(main_df.Project.unique())
    selected_param = main_df.columns.tolist()[2]
    slider_min = int(main_df[selected_param].min())
    slider_max = int(main_df[selected_param].max())
    slider_values = [slider_min, slider_max]

    if request.method == 'POST':
        selected_wikis = request.form['hidden_tags'].split(',')
        print(selected_wikis)
        selected_param = request.form['param']
        slider_values = [int(request.form['slider_min']), int(request.form['slider_max'])]

    filtered_df = main_df[main_df.Project.isin(selected_wikis)]
    figure = create_figure(filtered_df, selected_param, slider_values)

    graph_html = figure.to_html(full_html=False)

    return render_template('dashboard.html',
                           wikis=list(main_df.Project.unique()),
                           params=main_df.columns.tolist()[2:],
                           selected_wikis=selected_wikis,
                           selected_param=selected_param,
                           slider_min=slider_min,
                           slider_max=slider_max,
                           slider_values=slider_values,
                           graph_html=graph_html,
                           current_time=datetime.now().strftime("%B %Y"))

if __name__ == '__main__':
    app.run(debug=True)
