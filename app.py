from multiprocessing.sharedctypes import Value
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
# import numpy as np
import pandas as pd
# import matplotlib as mpl
import gunicorn                     #whilst your local machine's webserver doesn't need this, Heroku's linux webserver (i.e. dyno) does. I.e. This is your HTTP server
from whitenoise import WhiteNoise   #for serving static files on Heroku
import plotly.graph_objects as go

# Instantiate dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Reference the underlying flask app (Used by gunicorn webserver in Heroku production deployment)
server = app.server 

# Enable Whitenoise for serving static files from Heroku (the /static folder is seen as root by Heroku) 
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/') 


df_cif = pd.read_json('data/CIF_PU(2019-2022).json')
df_fob = pd.read_json('./data/FOB_PU(2019-2022).json')
def series(df, cnomen, cpais):
    meses = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC']
    return df[(df.CNOMEN == cnomen) & (df.CPAIS == cpais)][meses].iloc[0]
def series_multianios(df, cnomen, cpais, desde, hasta):
    s = []
    intervalo = list(range(desde, hasta+1, 1))
    for i, anio in enumerate(intervalo):
        s.append(series(df[df.CANIO==anio], cnomen, cpais))
        s[i].index = s[i].index +f'-{anio}'
    return pd.concat(s)

def grafico1():
    return(
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id="cnomen_dropdown",
                    options=list(df_cif.CNOMEN.unique()),
                    value=84410200,
                    clearable=False,
                ),
                dcc.Dropdown(
                    id="cpais_dropdown",
                    options=list(df_cif.CPAIS.unique()),
                    value="203",
                    clearable=False,
                ),
                dcc.RadioItems(
                    id="tipo-graf",
                    options = ['linea', 'barra'],
                    value='linea'),
                dcc.RangeSlider(min=2019,
                                max=2022,
                                step=1,
                                value=[2019, 2022],
                                marks={a:f'{a}' for a in range(2019,2023)},
                                id='intervalo'),
            ], className='plot-selector-container'),
            html.Div([
                dcc.Graph(id="graf")
                ],className='plot')
            

        ], className='plot-main-container')
    )


# Define Dash layout
def create_dash_layout(app):

    # Set browser tab title
    app.title = "Dashboard Fletes COMEX" 
    
    # Header
    header = html.Div([html.Br(), dcc.Markdown(""" # Probando"""), html.Br()])
    
    # Body 
    body = html.Div([
        dcc.Markdown(""" CIF VS FOB """),
        html.Br(),
        html.Div([
            grafico1(),
            # grafico2()        
            ],className='content-container')
        ])

    # Footer
    footer = html.Div([html.Br(), html.Br(), dcc.Markdown(""" ### Built with ![Image](heart.png) in Python using [Dash](https://plotly.com/dash/)""")])
    
    # Assemble dash layout 
    app.layout = html.Div([header, body, footer])

    return app

@app.callback(
    Output("graf", "figure"),
    [Input("cnomen_dropdown", "value"),
     Input("cpais_dropdown", "value"),
     Input("tipo-graf", "value"),
     Input("intervalo", "value")
     ]
    )
def update_chart(cnomen, cpais, tipo_graf, desde_hasta):
    desde, hasta= desde_hasta
    # width = [0.4]*12
    fig = go.Figure()

    if tipo_graf == "barra":
        
        fig.add_trace(go.Bar(x = series_multianios(df_cif, cnomen, cpais, desde, hasta).index,
                            y = series_multianios(df_cif, cnomen, cpais, desde, hasta),
                            # width = width,
                            name='CIF'))
        fig.add_trace(go.Bar(x = series_multianios(df_fob, cnomen, cpais, desde, hasta).index,
                            y = series_multianios(df_fob, cnomen, cpais, desde, hasta),
                            # width = width,
                            name='FOB'))


        fig.update_layout(title =  "CIF vs FOB",
                        barmode = 'group', title_font_size = 40,
                        )
    if tipo_graf == "linea":
        fig.add_trace(go.Scatter(x = series_multianios(df_cif, cnomen, cpais, desde, hasta).index,
                        y = series_multianios(df_cif, cnomen, cpais, desde, hasta),
                        # width = width,
                        name='CIF'))
        fig.add_trace(go.Scatter(x = series_multianios(df_fob, cnomen, cpais, desde, hasta).index,
                        y = series_multianios(df_fob, cnomen, cpais, desde, hasta),
                        # width = width,
                        name='FOB'))

        fig.update_layout(title =  "CIF vs FOB",
                    barmode = 'group', title_font_size = 40,
                    )
        
    return fig


# Construct the dash layout
create_dash_layout(app)

# Run flask app
if __name__ == "__main__": app.run_server(debug=False, host='0.0.0.0', port=8050)
