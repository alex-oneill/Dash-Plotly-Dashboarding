import dash_table
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import base64
import io
import numpy as np

app = dash.Dash()

# SECTION: CARDS
# NOTE: HEADER
header = dbc.Jumbotron(
            children=[
                html.H1('Visualizing Stock Movement', className='display-4', style={'textAlign': 'center'}),
                html.P('Project #2 | CS632P-Python Programming | Prof. Sarbanes',
                       className='lead', style={'textAlign': 'center'}),
                html.H4('Alex ONeill', style={'textAlign': 'center'})
            ], fluid=True, id='jumbotron_header', className='jumbotron', style={'paddingTop': '1rem',
                                                                                'paddingBottom': '1rem'})

# NOTE: FILE BROWSER
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
                    ], id='upload_body'),
                    dbc.CardFooter(id='card_footer')
                ], className='card text-white bg-dark mb-3', id='card_browser')

# NOTE: DATATYPE PICKER
data_picker = dbc.Card([
                    dbc.CardHeader('Select Columns', className='card text-white bg-primary mb-3'),
                    dbc.CardBody([], id='card-table-body')
                ], className='card text-white bg-dark mb-3', id='card_dataPicker')

# NOTE: DATA PREVIEW TABLE
preview = dbc.Card([
                    dbc.CardHeader('Data Preview', className='card text-white bg-primary mb-3'),
                    dbc.CardBody([
                        dcc.Dropdown(id='table_filter_dropdown', multi=True, placeholder='Select a benchmark',
                                     style={'color': '#55595c', 'fontFamily': 'monospace', 'textTransform': 'uppercase'}
                                     ),
                        html.Br(),
                        dt.DataTable(id='preview_table',
                                     style_header={'color': '#55595c', 'fontWeight': 'Bold', 'whiteSpace': 'normal',
                                                   'height': 'auto', 'textAlign': 'left'},
                                     style_data={'color': '#55595c', 'whiteSpace': 'normal', 'height': 'auto',
                                                 'textAlign': 'left'},
                                     style_table={'height': 300, 'overflowY': 'auto'},
                                     page_size=50)

                    ])
                ], className='card text-white bg-dark mb-3', id='card_dataPreview')

# NOTE: DISPLAY GRAPH
x = np.arange(10)
chart = dbc.Card([
                    dbc.CardHeader('Chart'),
                    dbc.CardBody([
                        dcc.Dropdown('asdf'), html.Br(),
                        dcc.Dropdown('asdfa23'),
                        html.Div('chart'),
                        dcc.Graph(figure=go.Figure(data=go.Scatter(x=x, y=x**2))) #, x='Date', y='Value'))
                    ])
                ], className='card text-white bg-dark mb-3', id='card_chart')


# SECTION: APP LAYOUT
app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(header)
            ]),
        dbc.Row([
            dbc.Col([
                file_browser,
                data_picker], width=4),
            dbc.Col([
                html.Div(id='hidden_data', style={'display': 'none'}),
                preview,
                chart], width=8)
        ])
], fluid=True)


# SECTION: UPLOAD SUCCESSFUL
@app.callback([Output('card_footer', 'children'),
               Output('upload', 'disabled')],
              Input('upload', 'filename'))
def show_filename(file_name):
    if not file_name:
        raise dash.exceptions.PreventUpdate
    else:
        text = 'File Uploaded: ' + file_name
        valid = dbc.Form(children=text, className='form-control is-valid', id='card_filename')
        upload_complete = [
            html.Div(valid),
            html.Br(),
            html.Div(
                dbc.Button(id='reset_button',
                           children='RESET',
                           className='btn btn-danger',
                           style={'width': '50%'})
                , style={'textAlign': 'center'})
        ]
        return upload_complete, True


# SECTION: PARSING UPLOAD DATA
@app.callback([Output('card-table-body', 'children'),
              Output('hidden_data', 'children')],
              Input('upload', 'contents'))
def parse_file(contents):
    if not contents:
        raise dash.exceptions.PreventUpdate
    else:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        cols = df.columns.tolist()
        dtypes = ['object/string', 'int64', 'float64', 'bool', 'datetime64']
        tbl_styles = {'verticalAlign': 'middle', 'textAlign': 'center'}
        headers = [
            html.Thead(
                html.Tr(
                    [html.Th('Column', style=tbl_styles),
                     html.Th('Type', style=tbl_styles),
                     html.Th('Ignore', style=tbl_styles)]
                )
            )
        ]
        id = 0
        for col in cols:
            toggle = dbc.Checklist(id='col_toggle_'+str(id),
                                   options=[{"label": "Drop", "value": 1}],
                                   value=[], switch=True)
            dropdown = dbc.Select(id='dtype_dropdown_'+str(id), placeholder='Select a dtype',
                                  options=[{'label': type, 'value': type} for type in dtypes],
                                  className='custom-select')
            headers.append(
                html.Tr(
                    [html.Td(col, style=tbl_styles),
                     html.Td(dropdown, style=tbl_styles),
                     html.Td(toggle, style=tbl_styles)]
                )
            )
            id += 1
        table = dbc.Table(headers, striped=True, bordered=True, className='table-secondary')
        return table, df.to_json(orient='split')


# SECTION: BUILD DYNAMIC TABLE
@app.callback([Output('preview_table', 'data'),
               Output('preview_table', 'columns'),
               Output('table_filter_dropdown', 'options')],
              Input('hidden_data', 'children'))
def make_preview_table(hidden_json_data):
    new_data = pd.read_json(hidden_json_data, orient='split')
    data = new_data.to_dict('records')
    column_headers = [{'name': key, 'id': key} for key in data[0].keys()]
    drop_tickers = [{'label': ticker, 'value': ticker} for ticker in new_data['Stock'].unique().tolist()]
    return data, column_headers, drop_tickers


# SECTION: RESET UPLOAD
# FIXME: NOT WORKING
# @app.callback([
#     Output('card_footer', 'children'),
#     Output('upload_body', 'children')],
#     Input('reset_button', 'active'))
# def reset_upload():
#     upload_body = [
#         dcc.Upload(
#             id='upload',
#             children=dbc.Button('Drag and Drop or Select to Upload',
#                                 className='btn btn-info'),
#             accept='.csv',
#             style={'textAlign': 'center', 'verticalAlign': 'middle'}),
#         html.Div(className='form-text text-muted', children='upload a CSV file to be used',
#                  style={'textAlign': 'center'})
#     ]
#     return '', upload_body


if __name__ == '__main__':
    app.run_server(debug=True)
