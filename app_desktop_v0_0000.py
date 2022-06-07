#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 22:04:08 2020

@author: Aron
"""





import os

import pandas as pd
import sys, arrow
import datetime

# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_daq as daq
# from dash.dependencies import Input, Output
# import dash_bootstrap_components as dbc


#import re
#import numpy as np
# from flask import Flask, request
from flask_caching import Cache


# Parse url
import urllib.parse as urlparse
from urllib.parse import parse_qs


# Worklist
# (1) Convert get_stock_data
# (2) stock_get_list, upload to database

# 設定工作目錄 .....


# Codebase
path_codebase = ['/Users/Aron/Documents/GitHub/Arsenal',
                 '/Users/Aron/Documents/GitHub/Codebase_YZ',
                 path, 
                 path + '/Function']


for i in path_codebase:    
    if i not in sys.path:
        sys.path = [i] + sys.path


import arsenal as ar
import codebase_yz as cbyz



# from app_master import app
import app_master as ms



# 自動設定區 -------
pd.set_option('display.max_columns', 30)



# from app import app


# layout = html.Div([
#     html.H3('App 2'),
#     dcc.Dropdown(
#         id='app-2-dropdown',
#         options=[
#             {'label': 'App 2 - {}'.format(i), 'value': i} for i in [
#                 'NYC', 'MTL', 'LA'
#             ]
#         ]
#     ),
#     html.Div(id='app-2-display-value'),
#     dcc.Link('Go to Desktop App', href='http://127.0.0.1:8050/'),    
# ])



colors = {
    'background': '#f5f5f5',
    'text': '#303030'
}


container_style = {
    'backgroundColor': colors['background'],
    'padding': '0 30px',
    'min-height': '650px',
    }


title_style = {
    'textAlign': 'left',
    'color': '#303030',
    'padding-top': '20px',
    'disply': 'inline-block',
    'width': '50%'
    }



debug_style = {
    'display': 'none',
    }




layout = html.Div([
    
    # dcc.Location(id='url', refresh=False),
    # html.P('Desktop Layout'),    


    # html.Div([
    #     dcc.Dropdown(
    #         id='name_dropdown',
    #         options=ms.stock_list,
    #         multi=True,
    #         value=[]
    #     ),
    # ],style=name_dropdown_style),
    
    # html.Div([
    #     html.P('半年資料'),
    #     daq.ToggleSwitch(
    #         id='btn_max',
    #         value=False,
    #         style={'padding':'0 10px'}
    #     ),
    #     html.P('三年資料'),
    # ], style=btn_max_style),        
    
    
    html.Div(id='debug', style=debug_style),
    
    # html.Div(
    #     dcc.Graph(id='main_graph'),
    #     id="line_chart"
    #     ),
    ]
    # style=container_style
)


# @app.callback(
#     Output('app-2-display-value', 'children'),
#     Input('app-2-dropdown', 'value'))
# def display_value(value):
#     return 'You have selected "{}"'.format(value)