import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash()

app.layout = html.Div(children=[
    # SECTION: HEADER
    html.H1(id='header', children='Adjust Close Price',
            style={
                'textAlign': 'center',
                'width': '98%',
                'border': 'solid'
            }),

    # SECTION: Row 1
    html.Div(children=[
        # SECTION: BROWSE FILE PATH
        html.H2(id='browser', children='Browse File Path',
                style={
                    'width': '29%',
                    'display': 'inline-block',
                    'border': 'solid'
                }),

        # SECTION: PREVIEW
        html.H2(id='data_preview', children='Preview the Data',
                style={
                    'width': '69%',
                    'display': 'inline-block',
                    'border': 'solid'
                })
    ]),
    html.Div(children=[
        # SECTION: SELECT COLUMNS
        html.H2(id='select_columns', children='Select the Columns to Keep',
                style={
                    'width': '29%',
                    'display': 'inline-block',
                    'border': 'solid'
                }),

        # SECTION: CHART
        html.H2(id='chart', children='Show Chart',
                style={
                    'width': '29%',
                    'display': 'inline-block',
                    'border': 'solid'
                })
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
