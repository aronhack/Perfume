# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 10:20:46 2022

@author: 吳雅智 Aron Wu
"""

# % 讀取套件 -------

import pandas as pd
import numpy as np
import sys, time, os, gc


import os
import pandas as pd
import numpy as np
import sys


# import dash
from dash import Dash, dash_table
from dash import dcc
from dash import html
# import dash_daq as daq
from dash.dependencies import Input, Output, State
import plotly.figure_factory as ff
# import dash_bootstrap_components as dbc

# import plotly.graph_objs as go
# from flask_caching import Cache

# import urllib.parse as urlparse
# from urllib.parse import parse_qs



# 設定工作目錄 .....
path = r'D:\GitHub\Perfume'
# path = r'/home/rserver/Data_Mining'


host = 2
host = 4


# Codebase
path_codebase = [path, 
                 path + '/Function',
                 'D:/Data_Mining/Projects/Codebase_YZ']

for i in path_codebase:    
    if i not in sys.path:
        sys.path = [i] + sys.path

    
import codebase_yz as cbyz
# import codebase_ml as cbml


import app_master_v0_0000 as ms
# import app_desktop_v0_0000 as desktop
# import mobile_app_v0_0000 as mobile



# 自動設定區 -------
pd.set_option('display.max_columns', 30)


# 新增工作資料夾
global path_resource, path_function, path_temp, path_export
path_resource = path + '/Resource'
path_function = path + '/Function'
path_temp = path + '/Temp'
path_export = path + '/Export'


cbyz.os_create_folder(path=[path_resource, path_function, 
                            path_temp, path_export])      




def dashboard(target):
    
    
    # Level 1. Search Note 
    # - Y:Price / X:heart note 
    # - X:heart note / Y:base note
    # - Description: name and link
    
    
    # Level 2. Associal Rule
    
    target = cbyz.conv_to_list(target)
    note_type = 'top_note'
    
    target_id_df = ms.note[ms.note['note'].isin(target)]
    target_id_df = target_id_df[['id']].drop_duplicates()
    target_id = target_id_df['id'].tolist()
    
    # Perfume List
    perfume_list = ms.data_raw[ms.data_raw['id'].isin(target_id)]


    # Heatmap
    
    return perfume_list



# %% Layout ----




# %% Application ----


app = Dash()

ms.master(host)
# ms.data_raw
# ms.perfume
# ms.note

dashboard(target=ms.unique_note)


if host == 2:
    cache = Cache(app.server, config={
        # try 'filesystem' if you don't want to setup redis
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })
    app.config.suppress_callback_exceptions = True
    

# Bug, not ms.perfume
# tb_cols = list(ms.perfume.columns)
tb_cols = [{"name": i, "id": i} for i in ms.perfume.columns]
tb_data = ms.perfume.to_dict('records')



# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
# app.layout = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
# [{"name": i, "id": i} for i in df.columns]

print(tb_data)


app.layout = html.Div([
    
    dcc.Location(id='url', refresh=False),
    html.Div(id='debug'),
    
    # Settings
    dcc.Input(id="device", type='hidden', value=0),    
    # dcc.Input(id="tick0", type='hidden', value=ms.first_date_lite),    
    dcc.Input(id="dtick", type='hidden', value=20),
    
    
    html.Div([
        dcc.Dropdown(
            id='note_selector',
            options=ms.unique_note,
            multi=True,
            value=[]
                ),
            ], 
        # style=stk_selector_style
        ),


    html.Div([dash_table.DataTable(
                id='perfume_list',
                columns=tb_cols,
                data=tb_data,
                ),    
            ], 
        # style=stk_selector_style
        ),


    # html.Div([
    #     html.P('半年資料'),
    #     daq.ToggleSwitch(
    #         id='data_period',
    #         value=False,
    #         style={'padding':'0 10px'}
    #     ),
    #     html.P('三年資料'),
    # ], style=data_period_style),      

    
    # html.Div(id='app_main', 
    #          style=app_main_style),
    
    # dcc.Graph(id="graph"),
    
    ]
)



# %% Callback ----


@app.callback(
    Output('debug', 'value'),
    # Output('dtick', 'value'),
    Input('note_selector', 'value'),
    # State('device', 'value')
)

def update_note(note):
    
    
    
    perfume_list = dashboard(note)
    print(perfume_list)
    
        
    
    
    data_matrix = [['Country', 'Year', 'Population'],
                   ['United States', 2000, 282200000],
                   ['Canada', 2000, 27790000],
                   ['United States', 2005, 295500000],
                   ['Canada', 2005, 32310000],
                   ['United States', 2010, 309000000],
                   ['Canada', 2010, 34000000]]
    
    fig = ff.create_table(data_matrix)
    fig.show()    



# Output(component_id='stk_selector', component_property='style'),
# Input(component_id='url', component_property='search'),

# @app.callback(
#     Output('stk_selector', 'style'),
#     Output('device', 'value'),    
#     Input('url', 'search'),
#     State('device', 'value'),
#     State('stk_selector', 'style')
# )


# def get_url(url, device, style):


#     if url == '':
#         device = 'desktop'
#         loc_style = stk_selector_style_desktop
#         return loc_style

    
#     parsed = urlparse.urlparse(url)
#     width = parse_qs(parsed.query)['w'][0]
    
    
#     if int(width) < 992:
#         device = 1
#         loc_style = stk_selector_style_mobile
#         print('mobile width')
#         # return mobile_app.layout
#     else:
#         device = 0
#         loc_style = stk_selector_style_desktop
#         print('desktop width')
#         # return desktop_app.layout
        

#     # return ''
#     return loc_style, device
        
    
# ................


# @app.callback(
#     Output('tick0', 'value'),
#     Output('dtick', 'value'),
#     Input('data_period', 'value'),
#     State('device', 'value')
# )

# def update_tick_attr(device, data_period):

#     # Update, different settings for desktop and mobile    
#     if device == 0:
#         if data_period:
#             return ms.first_date, 240
#         else:
#             return ms.first_date_lite, 60
#     else:
#         if data_period:
#             return ms.first_date, 240
#         else:
#             return ms.first_date_lite, 100       


# # ................


# @app.callback(
#     Output('graph', 'figure'),
#     Input('stk_selector', 'value'),
#     State('data_period', 'value'),
#     State('tick0', 'value'),
#     State('dtick', 'value'),    
#     State('device', 'value')
# )


# def update_output(dropdown_value, data_period, tick0, dtick, device):

#     # Figure ......
#     fig = go.Figure()
    
#     for i in range(len(dropdown_value)):

#         s = dropdown_value[i]  
#         name = ms.stock_list_raw[ms.stock_list_raw['STOCK_SYMBOL']==s]
#         name = name['STOCK'].tolist()[0]
        
        
#         # Filter Data ......
#         if data_period:
#             df = ms.main_data[ms.main_data['STOCK_SYMBOL']==s] \
#                 .reset_index(drop=True) 
#         else:
#             df = ms.main_data_lite[ms.main_data_lite['STOCK_SYMBOL']==s] \
#                 .reset_index(drop=True)    
                
#         trace = go.Candlestick(
#             x=df['WORK_DATE'],
#             open=df['OPEN'],
#             high=df['HIGH'],
#             low=df['LOW'],
#             close=df['CLOSE'],
#             name=name
#         )
        
#         fig.add_trace(trace)



#     # Layout ------
    
#     layout = {'plot_bgcolor': colors['background'],
#               'paper_bgcolor': colors['background'],
#               'font': {
#                   'color': colors['text']
#                   },
#               'xaxis':{'title':'日期',
#                        'fixedrange':True},
#               'yaxis':{'title':'收盤價',
#                        'fixedrange':True},
#               }


#     # Legend Layout ......
#     if device == 0:
#         legend_style = dict()    
#     else:
#         legend_style = dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         )
        

#     # 1. In plotly, there are rangebreaks to prevent showing weekends and 
#     #    holidays, but the weekends and holidays may be different in Taiwan. 
#     #    As a results, the alternative way to show it is to show as category
    
#     fig.layout = dict(xaxis={'type':"category", 
#                             'categoryorder':'category ascending',
#                             'tickmode':'linear',
#                             'tick0':tick0,
#                             'dtick':dtick,
#                             })

#     # Plotly doesn't have padding?
#     # 'padding':{'l':0, 'r':0, 't':20, 'b':20}

#     mobile_layout = {'legend':legend_style,
#                      'margin':{'l':36, 'r':36, 't':80, 'b':80}
#                      }

#     fig.update_layout(mobile_layout)
#     fig.update_layout(xaxis_rangeslider_visible=False)



#     return fig





# %% Exeture ------
    

# Version Note

# v0.0100
# - Add table

    
    
    

if __name__ == '__main__':
    
    app.run_server()
    # app.run_server(debug=True)







