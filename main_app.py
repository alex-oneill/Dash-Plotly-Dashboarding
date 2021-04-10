import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash()

header = dbc.Jumbotron(
            children=[
                html.H1('Header!', className='display-3', style={'textAlign': 'center'}),
                html.P('Use this page to visualize stock price data',
                       className='Lead', style={'textAlign': 'center'})
            ], fluid=True, id='jumbotron_header', style={'paddingTop': '1rem',
                                                         'paddingBottom': '1rem'})

file_browser = dbc.Card([
                    dbc.CardHeader('Browser', className='card text-white bg-primary mb-3'),
                    dbc.CardBody([
                        dcc.Upload(
                            id='upload',
                            children=dbc.Button('Drag and Drop or Select to Upload',
                                                className='btn btn-info'),
                            accept='.csv',
                            style={'textAlign': 'center', 'verticalAlign': 'middle'}),
                        html.Div(className='form-text text-muted', children='upload a CSV file to be used',
                            style={'textAlign': 'center'})
                    ]),
                    # dbc.CardFooter(children='', id='card_filename')
                    dbc.CardFooter(children='', id='card_filename')

                ], className='card text-white bg-dark mb-3', id='card_browser')

data_picker = dbc.Card([
                    dbc.CardHeader('Select Columns')
                ], className='card text-white bg-dark mb-3', id='card_dataPicker')

preview = dbc.Card([
                    dbc.CardHeader('Data Preview')
                ], className='card text-white bg-dark mb-3', id='card_dataPreview')

chart = dbc.Card([
                    dbc.CardHeader('Chart')
                ], className='card text-white bg-dark mb-3', id='card_chart')


app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(header)
            ]),
        dbc.Row([
            dbc.Col(file_browser, width=3),
            dbc.Col(preview)
        ]),
        dbc.Row([
            dbc.Col(data_picker, width=3),
            dbc.Col(chart)
        ])
], fluid=True)


@app.callback([Output('card_filename', 'children'),
               Output('upload', 'disabled')],
              Input('upload', 'filename'))
def show_filename(file_name):
    if not file_name:
        raise dash.exceptions.PreventUpdate
    else:
        text = 'File Uploaded: ' + file_name
        valid = dbc.Form(children=text, className='form-control is-valid', id='card_filename')
        return valid, True


if __name__ == '__main__':
    app.run_server(debug=True)
