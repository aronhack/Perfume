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
import plotly.express as px
import plotly.graph_objects as go
# import dash_daq as daq
from dash.dependencies import Input, Output, State
import plotly.figure_factory as ff

# from flask_caching import Cache
# import urllib.parse as urlparse
# from urllib.parse import parse_qs



# 設定工作目錄 .....
host = 1
# host = 4
# host = 0


if host == 0:
    path = r'/Users/aron/Documents/GitHub/Perfume'
elif host == 1:
    path = r'/home/aronhack/perfume'
elif host == 4:
    path = r'D:\GitHub\Perfume'


# Codebase
path_codebase = [path, 
                 path + '/Function',
                 r'/Users/aron/Documents/GitHub/Arsenal/',
                 r'/Users/aron/Documents/GitHub/Codebase_YZ',
                 r'D:/Data_Mining/Projects/Codebase_YZ',
                 r'D:\GitHub\Arsenal']

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



# %% Inner Function ------

def dashboard(top_note, heart_note, base_note):
    
    
    # Level 1. Search Note 
    # - Y:Price / X:heart note 
    # - X:heart note / Y:base note
    # - Description: name and link
    
    
    # Level 2. Associal Rule
    
    # top_note = '佛手柑'
    # heart_note = '佛手柑'
    # base_note = '佛手柑'
    
    # top_note = []
    # heart_note = []
    # base_note = []
    
    top_note = cbyz.conv_to_list(top_note)
    heart_note = cbyz.conv_to_list(heart_note)
    base_note = cbyz.conv_to_list(base_note)

    
    
    # 全部的note取交集
    target_id_df = ms.note.copy()
    
    if len(top_note) > 0:
        inner_id = target_id_df[(target_id_df['note'].isin(top_note)) \
                                   & (target_id_df['note_type']=='top_note')]
            
        inner_id = inner_id[['id']].drop_duplicates()
        target_id_df = target_id_df.merge(inner_id, how='inner', on='id')
    
    if len(heart_note) > 0:
        inner_id = target_id_df[(target_id_df['note'].isin(heart_note)) \
                                & (target_id_df['note_type']=='heart_note')]
    
        inner_id = inner_id[['id']].drop_duplicates()
        target_id_df = target_id_df.merge(inner_id, how='inner', on='id')
        
    if len(base_note) > 0:
        inner_id = target_id_df[(target_id_df['note'].isin(base_note)) \
                                & (target_id_df['note_type']=='base_note')]
    
        inner_id = inner_id[['id']].drop_duplicates()
        target_id_df = target_id_df.merge(inner_id, how='inner', on='id')    

    
    # target_id_df = target_id_df \
    #                 .groupby(['id']) \
    #                 .size() \
    #                 .reset_index(name='count')
    
    # target_id_df = target_id_df[target_id_df['count']==len(target)]
    target_id = target_id_df['id'].tolist()
    
    # Perfume List
    perfume_list = ms.data_raw[ms.data_raw['id'].isin(target_id)]
    
    # Perfume List
    perfume_list['name'] = '[' + perfume_list['name'] + '](' \
        + perfume_list['link'] + ')'    
    
    perfume_list = perfume_list[['id', 'brand', 'series', 'name',
                                 'price', 'top_note', 'heart_note',
                                 'base_note']]    
    
    
    cols = [{"name": i, "id": i} for i in perfume_list.columns]
    cols[3]['presentation'] = 'markdown'

    # Update, replace link    
    perfume_list_dict = perfume_list.to_dict('records')    


    # Heatmap ......
    print('Update - split heatmap as an independent function')
    print('Update - replace static top_note')
    heatmap_data_raw = ms.note[ms.note['id'].isin(target_id)]
    heatmap_data_raw = heatmap_data_raw[~heatmap_data_raw['note'].isin(top_note)]
    
    
    # Update, temporaily remove top_note
    heatmap_data_raw = heatmap_data_raw[heatmap_data_raw['note_type']!='top_note']
    # heatmap_data['count'] = 1
    
    
    heart_note = heatmap_data_raw[heatmap_data_raw['note_type']=='heart_note']
    heart_note = heart_note[['id', 'note']]
    heart_note.columns = ['id', 'heart_note']
    
    base_note = heatmap_data_raw[heatmap_data_raw['note_type']=='base_note']
    base_note = base_note[['id', 'note']]
    base_note.columns = ['id', 'base_note']    
    
    
    heatmap_data = cbyz.df_cross_join(heart_note, base_note, on='id')
    heatmap = gen_heatmap(heatmap_data)
    
    return perfume_list_dict, cols, heatmap



def gen_heatmap(heatmap_data, heatmap_num=10):

   # Limit number of note
    heatmap_data = heatmap_data \
                    .groupby(['heart_note', 'base_note']) \
                    .size() \
                    .reset_index(name='count')

    heatmap_data = heatmap_data \
                    .sort_values(by=['count'], ascending=False) \
                    .reset_index(drop=True) \
                    .reset_index()
                    
                    

    x = heatmap_data['base_note'].unique().tolist()
    x = x[:heatmap_num]
    
    y = heatmap_data['heart_note'].unique().tolist()
    y = y[:heatmap_num]
    
    heatmap_data = heatmap_data[(heatmap_data['base_note'].isin(x)) \
                                & (heatmap_data['heart_note'].isin(y))]
    
    # max_count可能是nan
    max_count = heatmap_data['count'].max()
    max_count = 10 if max_count != max_count else max_count
    print(max_count)
    
    heatmap_data = heatmap_data \
                    .pivot_table(index='heart_note',
                                  columns='base_note',
                                  values='count',
                                  fill_value=0) 

    # Set color
    # - color value是否要0-1
    # https://stackoverflow.com/questions/52903820/change-color-scheme-of-heatmap-in-plotly
    colors = [[0.0, '#F5FFFA'], 
              [0.2, '#ADD8E6'], 
              [0.4, '#87CEEB'],
              [0.6, '#87CEFA'], 
              [0.8, '#40E0D0'], 
              [1.0, '#00CED1']]

    x_note = '後調'
    y_note = '中調'

    layout = go.Layout(
        xaxis=dict(
            title=x_note
        ),
        yaxis=dict(
            title=y_note
        )) 


    heatmap = go.Figure(data=go.Heatmap(z=heatmap_data.values,
                                        x=x, y=y, hoverongaps=False,
                                        colorscale=colors),
                        layout=layout)
    
    return heatmap



# %% Layout ----




# %% Application ----
app = Dash()

ms.master(host)
# ms.data_raw
# ms.perfume
# ms.note

dashboard(top_note=[], heart_note=[], base_note=[])


if host == 2:
    cache = Cache(app.server, config={
        # try 'filesystem' if you don't want to setup redis
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })
    app.config.suppress_callback_exceptions = True
    

# Bug, not ms.perfume
# tb_cols = list(ms.perfume.columns)
# tb_data = ms.perfume.to_dict('records')

tb_data, tb_cols, heatmap = dashboard([], [], [])





app.layout = html.Div([
    
    dcc.Location(id='url', refresh=False),
    html.Div(id='debug'),
    
    # Settings
    dcc.Input(id="device", type='hidden', value=0),    
    # dcc.Input(id="tick0", type='hidden', value=ms.first_date_lite),    
    dcc.Input(id="dtick", type='hidden', value=20),
    

    html.Div([
        html.Label('前調'),
        dcc.Dropdown(
            id='top_note_selector',
            options=ms.unique_note,
            multi=True,
            value=[]
                ),
            ], 
        # style=stk_selector_style
        ),
    html.Div([
        html.Label('中調'),
        dcc.Dropdown(
            id='heart_note_selector',
            options=ms.unique_note,
            multi=True,
            value=[]
                ),
            ], 
        # style=stk_selector_style
        ),
    html.Div([
        html.Label('後調'),
        dcc.Dropdown(
            id='base_note_selector',
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
  
    html.Div([px.imshow([[1, 20, 30],
                 [20, 1, 60],
                 [30, 60, 1]])],
             id='heatmap'
             ),
    
    # html.Button('Convert', id='heatpmap_convert', n_clicks=0),
    
    
    dcc.Graph(id="graph",
              figure=heatmap),
    
    # id="graph",
    # [px.imshow([[1, 20, 30],
    #              [20, 1, 60],
    #              [30, 60, 1]])],
              
    
    ]
)



# %% Callback ----


@app.callback(
    # Output('debug', 'value'),
    Output('perfume_list', 'data'),
    Output('graph', 'figure'),
    Input('top_note_selector', 'value'),
    Input('heart_note_selector', 'value'),
    Input('base_note_selector', 'value'),
    # State('device', 'value')
)

def update_note(top_note, heart_note, base_note):
    tb_data, tb_cols, heatmap = dashboard(top_note, heart_note, base_note)
    
    return tb_data, heatmap
    
    




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
    

def version_note():
    
    # Version Note
    
    # v0.0100
    # - Add table
    # v0.0300
    # - Add selector for heart note and base note
    # - Add link

    # v0.0400
    # - Add axis conversion for heatmap

    
    # Worklist
    # - Evolve, daily backup for google sheet 
    # - Optimize, translation
    # - Optimize, filter the option of dropdown when selectiong others
    pass
    
    

if __name__ == '__main__':
    
    app.run_server()
    # app.run_server(debug=True)



