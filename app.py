from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

html.Title('Incubator Dashboard')
application = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

stats_path = 'stats/'
curr_time = datetime.now()
curr_file_path = f'{stats_path}{curr_time.strftime("%B").lower()}_{str(curr_time.year)}.tsv'
main_df = pd.read_csv(curr_file_path, sep='\t')

wikis_list = list(main_df.project.unique())
lang_list = ['(all)'] + list(main_df.sort_values('language code')['language code'].unique())
wiki_selector = dcc.Dropdown(wikis_list, value=wikis_list, multi=True)
sort_selector = dcc.Dropdown(['language code', 'Total number of edits', 'Total number of unique editors', 'Total number of pages', \
    'Average number of edits per month (last 3 months)', 'Average number of editors per month (last 3 months)', \
    'Total number of bytes added (last 30 days)', 'Total number of bytes removed (last 30 days)'], value='Total number of edits')

application.layout = dbc.Container([
    html.Br(),
    html.H1('Incubator Dashboard'),
    html.P('The dashboard gives an overview of activity of incubating projects on incubator.wikimedia.org.'),
    dbc.Row([
        dbc.Col([
            html.P('Project'),
            wiki_selector], md=7),
        dbc.Col([html.P('Sort by'),
                sort_selector], md=5)
    ]),
    html.Div(children=[dcc.Graph(id ='overview_table')], style = {'display': 'inline-block', 'width': '100%',}),
    dbc.Row([
        dbc.Col([
            html.P(f'The dashboard is updated bi-weekly and was last updated on {datetime.now()}')
        ], md=6),
        dbc.Col([
            html.P(f'Developed and maintained by KCVelaga and Jon Harald Søby')
        ], md=6)
    ])
])

@application.callback(
    Output('overview_table', 'figure'),
    Input(wiki_selector, 'value'),
    Input(sort_selector, 'value')
)
def update_overview_table(wiki_selection, sort_selection):
    overview_df = main_df[main_df.project.isin(wiki_selection)]
    if sort_selection == 'language code':
        overview_df = overview_df.sort_values(sort_selection)
    else:
        overview_df = overview_df.sort_values(sort_selection, ascending=False)
    overview_table = go.Figure(data=[go.Table(
        header=dict(values=list(overview_df.columns), align='left', fill_color='paleturquoise', font=dict(size=14)),
        cells=dict(values=[overview_df[col] for col in overview_df.columns], align='left', height=27.5,  fill_color='mintcream', font=dict(size=14)))
    ])
    overview_table.update_layout(height=1000)
    return overview_table

if __name__ == '__main__':
    application.run()

app = application.server