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

link_url = 'https://github.com/kcvelaga/IncubatorDashboard'
link = dcc.Link('Source Code', href=link_url, refresh=True)

overview_table = dash_table.DataTable(
    id='overview_table',
    columns=[{"name": i, "id": i} for i in main_df.columns],
    data=main_df.to_dict('records'),
    sort_action='native',
    sort_mode='single',
    style_table={
        'maxHeight': 'calc(50vh)',
    },
    style_header={
        'backgroundColor':'paleturquoise',
        'fontSize': '14px',
        'fontWeight': 'bold',
    },
    fixed_rows={'headers': True},
    style_cell={
        'textAlign': 'left',
        'fontFamily': 'Arial',
        'backgroundColor':'mintcream',
        'whiteSpace': 'normal',
        'height': '27.5px',
        'fontSize':'14px'
    },
    )

wikis_list = list(main_df.Project.unique())
# lang_list = ['(all)'] + list(main_df.sort_values('Language Code')['Language Code'].unique())
params = main_df.columns.tolist()[2:]
wiki_selector = dcc.Dropdown(wikis_list, value=wikis_list, multi=True)
param_selector = dcc.Dropdown(params, value=params[0], multi=False)
min = main_df[params[0]].min()
max = main_df[params[0]].max()



application.layout = dbc.Container([
    html.Br(),
    html.H1('Incubator Dashboard'),
    html.P('The dashboard gives an overview of activity of incubating projects on incubator.wikimedia.org.'),
    dbc.Row([
        dbc.Col([
            html.P('Project'),
            wiki_selector], md=7),
    ]),
    html.Br(),
dbc.Row([dbc.Col([param_selector],md=4),
dbc.Col([dcc.RangeSlider(min=min, max=max, step=1, value=[min, max],
               id='range-slider',
               marks=None,
               allowCross=False,
               updatemode='mouseup',
               tooltip={"placement": "left", "always_visible": True,},
    )],md=8),
]),
    html.Br(),
    dbc.Row(
        dbc.Col(
            overview_table
),
),
html.Br(),
    dbc.Row([
        dbc.Col([
           html.P(f'The dashboard is updated monthly and was last updated on {datetime.now().strftime("%B")} {datetime.now().year}')
        ]),
        dbc.Col([
            link
        ],md=2,className='text-right')
    ])
])

@application.callback(
    Output('overview_table', 'data'),
    Output('range-slider', 'marks'),
    Output('range-slider', 'min'),
    Output('range-slider', 'max'),
    Input(wiki_selector, 'value'),
    Input(param_selector, 'value'),
    Input('range-slider', 'value'),
)
def update_overview_table(wiki_selection, param_selection,slider_value):
    print(slider_value)
    overview_df = main_df[main_df.Project.isin(wiki_selection)]
    overview_df_copy = overview_df.copy()
    overview_df = overview_df[(overview_df[param_selection] >= slider_value[0]) & (overview_df[param_selection] <= slider_value[1])]

    overview_table = go.Figure(data=[go.Table(
        header=dict(values=list(overview_df.columns), align='left', fill_color='paleturquoise', font=dict(size=14)),
        cells=dict(values=[overview_df[col] for col in overview_df.columns], align='left', height=27.5,  fill_color='mintcream', font=dict(size=14)))
    ])

    
    min_value = int(overview_df_copy[param_selection].min())
    max_value = int(overview_df_copy[param_selection].max())
    # slider_value = [min_value,max_value]

    marks = {
        min_value: str(min_value),
        max_value: str(max_value),
    }

    slider_marks = marks.copy()
    slider_marks[slider_value[0]] = str(slider_value[0])
    slider_marks[slider_value[1]] = str(slider_value[1])

    overview_table.update_layout(height=1000)
    data = overview_df.to_dict('records')
    return data,marks,min_value, max_value

if __name__ == '__main__':
    application.run_server(debug=True)

app = application.server
