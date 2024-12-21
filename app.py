from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd
import os
import glob

application = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='WM Incubator Stats')
# application = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


data_files = glob.glob("stats/*.tsv")

def extract_dt_from_filename(filename):
    base = os.path.basename(filename)
    date_str = base.split(".")[0]
    return datetime.strptime(date_str, "%Y-%m-%d").date()

dated_files = [(f, extract_dt_from_filename(f)) for f in data_files]
sorted_data_files = sorted(dated_files, key=lambda x: x[1])

latest_stats, latest_dt = sorted_data_files[-1]
stats = pd.read_csv(latest_stats, sep="\t").drop('Prefix', axis=1)

source_code_url = "https://github.com/indictechcom/wm-incubator-stats"

for col in stats.columns:
    if col not in ['Project', 'Language Code']:
        stats[col] = pd.to_numeric(stats[col], errors='coerce').fillna(0)

stats_tbl = dash_table.DataTable(
    id="stats_tbl",
    columns=[{"name": i, "id": i} for i in stats.columns],
    data=stats.to_dict("records"),
    sort_action="native",
    sort_mode="single",
    page_size=15,
    page_action="none",
    style_table={"height": "500px", "overflowY": "auto", "border": "1px solid #e3e3e3"},
    style_as_list_view=True,
    style_header={
        "backgroundColor": "#f7f7f7",
        "fontWeight": "bold",
        "borderBottom": "2px solid #d3d3d3",
        "fontSize": "16px",
        "textAlign": "center",
    },
    style_cell={
        "padding": "10px",
        "backgroundColor": "#ffffff",
        "color": "#333333",
        "fontFamily": "Arial, sans-serif",
        "fontSize": "14px",
        "border": "1px solid #e3e3e3",
        "textAlign": "right",
    },
    style_cell_conditional=[
        {"if": {"column_id": ["Project", "Language Code"]}, "fontWeight": "bold", "textAlign": "center"},
    ],
    style_data={"border": "1px solid #e3e3e3"},
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "#f7f7f7"},
        {"if": {"row_index": "even"}, "backgroundColor": "#ffffff"},
        {"if": {"state": "selected"}, "backgroundColor": "#eaf2ff", "border": "1px solid #0074d9"},
    ],
)

project_groups = list(stats["Project"].unique())
default_selection = project_groups  # Default to all projects selected
project_group_selector = dcc.Dropdown(
    project_groups, value=default_selection, multi=True, id='project-group-selector'
)

all_cols = stats.columns.tolist()
identifier_cols = ["Project", "Language Code"]
stats_cols = [col for col in all_cols if col not in identifier_cols]
filter_col_selector = dcc.Dropdown(
    stats_cols, value=stats_cols[0], multi=False
)

application.layout = dbc.Container(
    [
        html.Br(),
        html.H1("Wikimedia Incubator Stats Dashboard"),
        html.P(
            [
                "The dashboard gives an overview of key activity metrics of incubating projects on ",
                html.A(
                    "incubator.wikimedia.org",
                    href="https://incubator.wikimedia.org/",
                    target="_blank",
                    style={"color": "#007BFF", "text-decoration": "none"},
                ),
                ".",
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col([html.P("Select project(s)"), project_group_selector], md=7),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                html.P("Filter"),
                dbc.Col([filter_col_selector], md=4),
                dbc.Col(
                    [
                        dcc.RangeSlider(
                            id="range-slider",
                            marks=None,
                            allowCross=False,
                            updatemode="mouseup",
                            tooltip={"placement": "left", "always_visible": True},
                        )
                    ],
                    md=8,
                ),
            ]
        ),
        html.Br(),
        html.H4("Statistics"),
        dbc.Row(
            dbc.Col(stats_tbl),
        ),
        html.Br(),
        dbc.Row(
            [
                html.P("Notes:"),
                html.Ul(
                    [
                        html.Li("Edits, Editors, Page: all time counts"),
                        html.Li("Bytes added/removed: last 30 days"),
                        html.Li("Avg monthly edits/editors: last 3 months"),
                    ],
                    style={"padding-left": "20px", "list-style-position": "inside"},
                ),
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                html.P(
                    [
                        f"The data is usually updated weekly and was last updated on {latest_dt}.",
                        " | Developed and maintained by ",
                        html.A(
                            "KCVelaga",
                            href="https://www.mediawiki.org/w/index.php?title=User:KCVelaga",
                            target="_blank",
                            style={"color": "#007BFF", "text-decoration": "none"},
                        ),
                        " (",
                        dcc.Link("source code", href=source_code_url, refresh=True),
                        ")",
                    ]
                )
            ]
        ),
    ]
)

@application.callback(
    Output('project-group-selector', 'value'),
    Input('project-group-selector', 'value'),
    prevent_initial_call=True 
)
def ensure_selection_not_empty(selected_projects):
    if not selected_projects:
        return default_selection
    return selected_projects

@application.callback(
    Output("range-slider", "min"),
    Output("range-slider", "max"),
    Output("range-slider", "marks"),
    Output("range-slider", "value"),
    Input(project_group_selector, "value"),
    Input(filter_col_selector, "value"),
)
def update_slider_range(wiki_selection, param_selection):
    if not wiki_selection:
        wiki_selection = default_selection

    filtered_df = stats[stats["Project"].isin(wiki_selection)]
    min_value = int(filtered_df[param_selection].min())
    max_value = int(filtered_df[param_selection].max())
    marks = {min_value: str(min_value), max_value: str(max_value)}
    value = [min_value, max_value]
    return min_value, max_value, marks, value

@application.callback(
    Output("stats_tbl", "data"),
    Input(project_group_selector, "value"),
    Input(filter_col_selector, "value"),
    Input("range-slider", "value"),
)
def update_table_data(wiki_selection, param_selection, slider_value):
    if not wiki_selection:
        wiki_selection = default_selection

    df = stats[stats["Project"].isin(wiki_selection)]
    df_filtered = df[
        (df[param_selection] >= slider_value[0])
        & (df[param_selection] <= slider_value[1])
    ]
    return df_filtered.to_dict("records")

if __name__ == '__main__':
    application.run_server()

app = application.server