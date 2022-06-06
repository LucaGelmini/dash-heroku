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


# Define Dash layout
def create_dash_layout(app):

    # Set browser tab title
    app.title = "Your app title" 
    
    # Header
    header = html.Div([html.Br(), dcc.Markdown(""" # Hi. I'm your Dash app."""), html.Br()])
    
    # Body 
    body = html.Div([
        dcc.Markdown(""" ## I'm ready to serve static files on Heroku. Just look at this! """),
        html.Br(),
        html.Img(src='charlie.png'),
        html.Br(),
        html.Button(id="boton", value=True),
        dcc.Graph(id="pruebita")
        ])

    # Footer
    footer = html.Div([html.Br(), html.Br(), dcc.Markdown(""" ### Built with ![Image](heart.png) in Python using [Dash](https://plotly.com/dash/)""")])
    
    # Assemble dash layout 
    app.layout = html.Div([header, body, footer])

    return app

@app.callback(
    Output("pruebita", "figure"),
    Input('boton','value')
)
def update_chart(boton):
    a= pd.DataFrame({'b': [1,2,3], 'c': [3,5,2]})
    app.logger.info('holaaa')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1,2,3], y=[3,5,2]))
    
    fig.update_layout(title =  "pruebita",
                  title_font_size = 40,
                )
    return fig


# Construct the dash layout
create_dash_layout(app)

# Run flask app
if __name__ == "__main__": app.run_server(debug=False, host='0.0.0.0', port=8050)
