"""
Author: ALEX ONEILL
CS632P - Python Programming (Prof. Sarbanes)
Project 2 - Visualizing Stock Data with Dash/Plotly
"""

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import io


app = dash.Dash(__name__, suppress_callback_exceptions=True)

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

# NOTE: FILE BROWSER CARD
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

# NOTE: DATATYPE PICKER CARD
data_picker = dbc.Card([
                    dbc.CardHeader('Select Columns', className='card text-white bg-primary mb-3'),
                    dbc.CardBody(id='data_picker_card_body',
                                 children=dbc.Table(bordered=True, className='table-secondary',
                                                    id='data_picker_table')),
                    dbc.CardFooter(id='picker_footer', style={'textAlign': 'center', 'verticalAlign': 'middle'}),
                    dbc.CardFooter(id='picker_footer_2', style={'textAlign': 'center', 'verticalAlign': 'middle'})
                ], className='card text-white bg-dark mb-3', id='card_dataPicker')

# NOTE: DATA PREVIEW TABLE CARD
dropdown_style = {'color': '#55595c', 'fontFamily': 'monospace', 'textTransform': 'uppercase'}
preview = dbc.Card([
                    dbc.CardHeader('Data Preview', className='card text-white bg-primary mb-3'),
                    dbc.CardBody([
                        dcc.Dropdown(id='table_filter_dropdown', multi=True, placeholder='Select a security',
                                     style=dropdown_style),
                        html.Br(),
                        dt.DataTable(id='preview_table',
                                     style_header={'color': '#55595c', 'fontWeight': 'Bold', 'whiteSpace': 'normal',
                                                   'height': 'auto', 'textAlign': 'left'},
                                     style_data={'color': '#55595c', 'whiteSpace': 'normal', 'height': 'auto',
                                                 'textAlign': 'left'},
                                     style_table={'height': 300, 'overflowY': 'auto'},
                                     page_size=50)
                    ]),
                    dbc.CardFooter(id='preview_footer', style={'textAlign': 'center', 'verticalAlign': 'middle'})
                ], className='card text-white bg-dark mb-3', id='card_dataPreview')

# NOTE: DISPLAY GRAPH CARD
chart = dbc.Card([
                    dbc.CardHeader('Chart', className='card text-white bg-primary mb-3'),
                    dbc.CardBody([
                        dcc.Dropdown(disabled=True, style=dropdown_style, placeholder='Select a feature',
                                     id='chart_dd'),
                        html.Br(),
                        dcc.Dropdown(disabled=True, style=dropdown_style, placeholder='Select a security',
                                     id='chart_dd2', multi=True),
                        html.Br(),
                        dcc.Graph(id='px_figure')
                    ])
                ], className='card text-white bg-dark mb-3', id='card_chart')

# SECTION: APP LAYOUT
tbl_styles = {'verticalAlign': 'middle', 'textAlign': 'center'}
app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(header)
            ]),
        dbc.Row([
            dbc.Col([
                file_browser,
                data_picker], width=4),
            dbc.Col([
                html.Div(id='hidden_df', style={'display': 'none'}),
                html.Div(id='hidden_fdf_1', style={'display': 'none'}),
                html.Div(id='hidden_fdf_final', style={'display': 'none'}),
                html.Div(id='printer_list', style={'display': 'none'}, children=[]),
                html.Div(id='df_config', style={'display': 'none'}),
                preview,
                chart], width=8)
        ])
], fluid=True)


# SECTION: CALLBACKS
# NOTE: 1--UPLOAD SUCCESSFUL // RESET BUTTON
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
            html.Div(valid), html.Br(), html.Div(dbc.Button(id='reset_button', children='RESET',
                                                            className='btn btn-danger', style={'width': '50%'}),
                                                 style={'textAlign': 'center'})]
        return upload_complete, True


# NOTE: 2--STORE UPLOADED DF
@app.callback(Output('hidden_df', 'children'),
              Input('upload', 'contents'))
def parse_full_file(contents):
    if not contents:
        raise dash.exceptions.PreventUpdate
    else:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        return df.to_json(orient='split')


# NOTE: 3--MAKE PICKER TABLE
@app.callback([Output('data_picker_table', 'children'),
               Output('picker_footer', 'children')],
              Input('hidden_df', 'children'))
def make_picker_table(hidden_df):
    df = pd.read_json(hidden_df, orient='split')
    cols = df.columns.tolist()
    headers = [
        html.Thead(html.Tr([html.Th('Column', style=tbl_styles), html.Th('Casted Type', style=tbl_styles),
                            html.Th('Ignore', style=tbl_styles)]))]
    id = 0
    for col in cols:
        if df[col].dtype == 'datetime64[ns]':
            dropdown = dbc.Select(id='dtype_dropdown_' + str(id), placeholder='Casted dtype',
                                  options=[{'label': 'datetime64', 'value': 'datetime64'},
                                           {'label': 'object/string', 'value': 'object'}],
                                  className='custom-select')
        elif df[col].dtype == 'int64' or df[col].dtype == 'float64':
            dropdown = dbc.Select(id='dtype_dropdown_'+str(id), placeholder='Casted dtype',
                                  options=[{'label': 'int64', 'value': 'int64'},
                                           {'label': 'float64', 'value': 'float64'},
                                           {'label': 'object/string', 'value': 'object'}],
                                  className='custom-select')
        elif df[col].dtype == 'object':
            dropdown = dbc.Select(id='dtype_dropdown_'+str(id), placeholder='Casted dtype',
                                  options=[{'label': 'object/string', 'value': 'object'}],
                                  className='custom-select')
        toggle = dbc.Checklist(id='column_toggle_' + str(id),
                               options=[{'label': 'Drop', 'value': 1}],
                               switch=True)
        headers.append(
            html.Tr(id='data_row_'+str(id),
                    children=[html.Td(col, style=tbl_styles, id='col_name_'+str(id)),
                              html.Td(dropdown, style=tbl_styles),
                              html.Td(toggle, style=tbl_styles)]))
        id += 1
    drop_cols = dbc.Button('Confirm Dropped Rows', className='btn btn-warning', id='confirm_dropped_rows',
                           style={'width': '50%'})
    return headers, drop_cols


# NOTE: 4--DROP COLUMNS FOR PREVIEW
@app.callback([Output('hidden_fdf_1', 'children'),
               Output('picker_footer_2', 'children'),
               Output('confirm_dropped_rows', 'disabled')],
              Input('confirm_dropped_rows', 'n_clicks'),
              [State('hidden_df', 'children')] + [(State('column_toggle_'+str(num), 'value')) for num in range(5)])
def drop_cols(n_clicks, hidden_df, col0, col1, col2, col3, col4):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate()
    elif n_clicks > 0:
        cols = [col0, col1, col2, col3, col4]
        temp_data = pd.read_json(hidden_df, orient='split')
        col_names = temp_data.columns.tolist()
        for i, col in enumerate(cols):
            if col:
                temp_data.drop(columns=col_names[i], inplace=True)
        cast_cols = dbc.Button('Confirm Casted Types', className='btn btn-warning', id='confirm_casts',
                               style={'width': '50%'})
        return temp_data.to_json(orient='split'), cast_cols, True


# NOTE: 5--CAST COLUMNS FOR PREVIEW
@app.callback([Output('hidden_fdf_final', 'children'),
               Output('confirm_casts', 'disabled')],
              Input('confirm_casts', 'n_clicks'),
              [State('hidden_fdf_1', 'children')] + [(State('dtype_dropdown_'+str(num), 'value')) for num in range(5)] +
              [State('hidden_df', 'children')])
def cast_cols(n_clicks, hidden_df, col0, col1, col2, col3, col4, orig_df):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate()
    elif n_clicks > 0:
        cols = [col0, col1, col2, col3, col4]
        temp_data = pd.read_json(hidden_df, orient='split')
        orig = pd.read_json(orig_df, orient='split')
        orig_col_names = orig.columns.tolist()
        for i, dtype in enumerate(cols):
            if dtype:
                col_name = orig_col_names[i]
                temp_data[col_name] = temp_data[col_name].astype(dtype)
        return temp_data.to_json(orient='split'), True


# NOTE: 6--PREVIEW TABLE DROPDOWN
@app.callback(Output('table_filter_dropdown', 'options'),
              Input('hidden_fdf_final', 'children'))
def make_preview_table_dropdown(hidden_json_data):
    new_data = pd.read_json(hidden_json_data, orient='split')
    drop_tickers = [{'label': ticker, 'value': ticker} for ticker in new_data['Stock'].unique().tolist()]
    return drop_tickers


# NOTE: 7--PREVIEW TABLE
@app.callback([Output('preview_table', 'data'),
               Output('preview_table', 'columns'),
               Output('preview_footer', 'children')],
              Input('table_filter_dropdown', 'value'),
              State('hidden_fdf_final', 'children'))
def make_preview_table(securities, hidden_json_data):
    if not hidden_json_data:
        raise dash.exceptions.PreventUpdate
    else:
        new_data = pd.read_json(hidden_json_data, orient='split')
        data = new_data.to_dict('records')
        column_headers = [{'name': key, 'id': key} for key in data[0].keys()]
        fdf = new_data.loc[new_data['Stock'].isin(securities)]
        data = fdf.to_dict('records')
        chart_button = dbc.Button('Activate Charting Options', className='btn btn-success', id='build_chart',
                                  style={'width': '50%'})
        return data, column_headers, chart_button


# NOTE: 8--ACTIVATE CHART DROPDOWNS
@app.callback([Output('chart_dd', 'options'),
               Output('chart_dd', 'disabled'),
               Output('chart_dd2', 'options'),
               Output('chart_dd2', 'disabled'),
               Output('build_chart', 'disabled')],
              Input('build_chart', 'n_clicks'),
              State('hidden_df', 'children'))
def make_chart(click, hidden_json_data):
    if not hidden_json_data or not click:
        raise dash.exceptions.PreventUpdate
    elif click > 0:
        new_data = pd.read_json(hidden_json_data, orient='split')
        dd1_options = [{'label': col, 'value': col} for col in ['Volume', 'Adj Close']]
        dd2_options = [{'label': ticker, 'value': ticker} for ticker in new_data['Stock'].unique().tolist()]
        return dd1_options, False, dd2_options, False, True


# NOTE: 9--FILTERING CHART DISPLAY
@app.callback(Output('px_figure', 'figure'),
              [Input('chart_dd', 'value'),
               Input('chart_dd2', 'value')],
              State('hidden_df', 'children'))
def filter_chart(feature, securities, data):
    if not feature or not securities or not data:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_json(data, orient='split')
        fdf = df.loc[df['Stock'].isin(securities)]
        data = fdf.to_dict('records')
        fig_out = px.line(data, x='Date', y=feature, color='Stock')
        return fig_out


if __name__ == '__main__':
    app.run_server(debug=True)
