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
import dash_bootstrap_components as dbc

# import dash_daq as daq
from dash.dependencies import Input, Output, State
import plotly.figure_factory as ff

from flask_caching import Cache
# import urllib.parse as urlparse
# from urllib.parse import parse_qs



# 設定工作目錄 .....
host = 1
host = 4
host = 0


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

def dashboard(top_note, heart_note, base_note, status=0):
    
    
    # Level 1. Search Note 
    # - Y:Price / X:heart note 
    # - X:heart note / Y:base note
    # - Description: name and link
    
    
    # Level 2. Associal Rule
    # top_note = '佛手柑'
    # top_note = '檸檬'
    # top_note = ['檸檬', '橙花']
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
    
    note_li = [top_note, heart_note, base_note]
    note_str_li = ['top_note', 'heart_note', 'base_note']
    
    
    for i in range(3):
        
        cur_note = note_li[i]
        cur_note_str = note_str_li[i]
        if len(cur_note) > 0:
            inner_id = target_id_df[(target_id_df['note'].isin(cur_note)) \
                                       & (target_id_df['note_type']==cur_note_str)]
                
            # Ensure the perfume containing all the notes
            inner_id = inner_id \
                        .groupby(['id']) \
                        .size() \
                        .reset_index(name='count')
            
            inner_id = inner_id[inner_id['count']==len(cur_note)]
            target_id_df = target_id_df.merge(inner_id, how='inner', on='id')

    target_id = target_id_df['id'].unique().tolist()
    
    # Perfume List
    perfume_list = ms.data_raw[ms.data_raw['id'].isin(target_id)]
    perfume_list['name'] = '[' + perfume_list['name'] + '](' \
                            + perfume_list['link'] + ')'    
    
    perfume_list = perfume_list[['brand', 'series', 'name',
                                 'top_note', 'heart_note', 'base_note']]
    
    perfume_list.columns = ['品牌', '系列', '名稱', '前調', '中調', '後調']
    
    
    cols = [{"name": i, "id": i} for i in perfume_list.columns]
    cols[2]['presentation'] = 'markdown'

    print('Update, replace link') 
    perfume_list_dict = perfume_list.to_dict('records')    


    # Heatmap ......
    heatmap_data_raw = ms.note[ms.note['id'].isin(target_id)]


    if status == 0:
        heatmap_data_raw = heatmap_data_raw[heatmap_data_raw['note_type']!='top_note']
        x_note = 'base_note'
        y_note = 'heart_note'
        
    elif status == 1:
        heatmap_data_raw = heatmap_data_raw[heatmap_data_raw['note_type']!='heart_note']
        x_note = 'base_note'
        y_note = 'top_note'
        
    elif status == 2:
        heatmap_data_raw = heatmap_data_raw[heatmap_data_raw['note_type']!='base_note']
        x_note = 'heart_note'
        y_note = 'top_note'
    
    x_note_df = heatmap_data_raw[heatmap_data_raw['note_type']==x_note]
    x_note_df = x_note_df[['id', 'note']]
    x_note_df.columns = ['id', 'x_note']
    
    y_note_df = heatmap_data_raw[heatmap_data_raw['note_type']==y_note]
    y_note_df = y_note_df[['id', 'note']]
    y_note_df.columns = ['id', 'y_note']    
    
    heatmap_data = cbyz.df_cross_join(x_note_df, y_note_df, on='id')
    heatmap_data, heatmap = gen_heatmap(heatmap_data, status)
    
    return perfume_list_dict, cols, heatmap_data, heatmap



def gen_heatmap(heatmap_data, status, heatmap_num=10):

   # Limit number of note
    heatmap_data = heatmap_data \
                    .groupby(['x_note', 'y_note']) \
                    .size() \
                    .reset_index(name='count')

    heatmap_data = heatmap_data \
                    .sort_values(by=['count'], ascending=False) \
                    .reset_index(drop=True) \
                    .reset_index()
                    

    x = heatmap_data['x_note'].unique().tolist()
    x = x[:heatmap_num]
    
    y = heatmap_data['y_note'].unique().tolist()
    y = y[:heatmap_num]
    
    heatmap_data = heatmap_data[(heatmap_data['x_note'].isin(x)) \
                                & (heatmap_data['y_note'].isin(y))]
    
    # max_count可能是nan
    max_count = heatmap_data['count'].max()
    max_count = 10 if max_count != max_count else max_count
    print(max_count)
    
    heatmap_data = heatmap_data \
                    .pivot_table(index='y_note',
                                  columns='x_note',
                                  values='count',
                                  fill_value=0) 
                    

    x_label = list(heatmap_data.columns)
    y_label = list(heatmap_data.index)            

    # In general, Dash properties can only be dash components, strings, 
    # dictionaries, numbers, None, or lists of those.                    
    heatmap_data = heatmap_data.values  
    # Set color
    # - color value是否要0-1
    # https://stackoverflow.com/questions/52903820/change-color-scheme-of-heatmap-in-plotly
    colors = [[0.0, '#F5FFFA'], 
              [0.2, '#ADD8E6'], 
              [0.4, '#87CEEB'],
              [0.6, '#87CEFA'], 
              [0.8, '#40E0D0'], 
              [1.0, '#00CED1']]

    if status == 0:
        x_note = '後調'
        y_note = '中調'
        
    elif status == 1:
        x_note = '後調'
        y_note = '前調'
        
    elif status == 2:
        x_note = '中調'
        y_note = '前調'
    

    layout = go.Layout(
        xaxis=dict(
            title=x_note
        ),
        yaxis=dict(
            title=y_note
        ),
        height=800
        ) 


    heatmap = go.Figure(data=go.Heatmap(z=heatmap_data,
                                        x=x_label, y=y_label, hoverongaps=False,
                                        colorscale=colors),
                        layout=layout)
    
    return heatmap_data, heatmap



# %% Layout ----

note_selector_css = {
    # 'width': '50%', 
    'padding-top': '40px', 
    'display': 'block',
    }

print('Evolve, fix table layout as width by 100%')
table_css = {
    'width': '100%',
    # 'margin-left': '5%',
    # 'margin-right': '5%' 
    }




# %% Application ----
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

ms.master(host)
# ms.data_raw
# ms.perfume
# ms.note

dashboard(top_note=[], heart_note=[], base_note=[])


if host == 1:
    cache = Cache(app.server, config={
        # try 'filesystem' if you don't want to setup redis
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })
    app.config.suppress_callback_exceptions = True
    

# Bug, not ms.perfume
# tb_cols = list(ms.perfume.columns)
# tb_data = ms.perfume.to_dict('records')

tb_data, tb_cols, init_heatmap_data, init_heatmap = dashboard([], [], [])





app.layout = html.Div([
    
    dcc.Location(id='url', refresh=False),
    html.Div(id='debug'),
    
    # Settings
    dcc.Input(id="device", type='hidden', value=0),    
    # dcc.Input(id="tick0", type='hidden', value=ms.first_date_lite),    
    dcc.Input(id="dtick", type='hidden', value=20),
    


    dbc.Row([
        
        dbc.Col(
            html.Div([
                html.Label('前調'),
                dcc.Dropdown(
                    id='top_note_selector',
                    options=ms.unique_note,
                    multi=True,
                    value=[]
                        ),
                    ], 
                style=note_selector_css
                ),
            width=12,
            md=4
            ),


        dbc.Col(
            html.Div([
                html.Label('中調'),
                dcc.Dropdown(
                    id='heart_note_selector',
                    options=ms.unique_note,
                    multi=True,
                    value=[]
                        ),
                    ], 
                style=note_selector_css
                ),
            width=12,
            md=4
            ),

        dbc.Col(
            html.Div([
                html.Label('後調'),
                dcc.Dropdown(
                    id='base_note_selector',
                    options=ms.unique_note,
                    multi=True,
                    value=[]
                        ),
                    ], 
                style=note_selector_css
                ),
            width=12,
            md=4
            ),
        ],
        className='',
    ),

    html.Div([dash_table.DataTable(
                id='perfume_list',
                columns=tb_cols,
                data=tb_data,
                style_cell={'textAlign': 'left'},
                ),    
            ], 
        style=table_css,
        # className='text-left'
        ),

    dcc.Input(id="heatmap_status", type='hidden', value=0),        
    html.Button('切換', id='heatpmap_convert', n_clicks=0),
    
    dcc.Store(id='heatmap_data'),
    dcc.Graph(id="graph", figure=init_heatmap),
    
    html.Div(html.Span('Created by Angel & Aron', className='d-block'),
             className='text-center my-2')
    ]
)



# %% Callback ----

@app.callback(
    # Output('debug', 'value'),
    Output('perfume_list', 'data'),
    Output('heatmap_status', 'value'),
    # Output('heatmap_data', 'data'),
    Output('graph', 'figure'),
    Input('top_note_selector', 'value'),
    Input('heart_note_selector', 'value'),
    Input('base_note_selector', 'value'),
    Input('heatpmap_convert', 'n_clicks'),
    State('heatmap_status', 'value')
)

def update_note(top_note, heart_note, base_note, 
                clicks, status):

    print('clicks', clicks)
    
    if status == 2:
        status = 0
    else:
        status = status + 1


    tb_data, tb_cols, heatmap_data, heatmap = \
        dashboard(top_note, heart_note, base_note, status)


    
    # return tb_data, heatmap_data, heatmap
    return tb_data, status, heatmap
    


# %% Debug ------

def debug():
    
    debug_df =  ms.data_raw.copy()
    debug_df = debug_df[debug_df['top_note'].str.contains('佛手柑')]
    
    pass


# %% Exetue ------
    

def version_note():
    
    # Version Note
    
    # v0.0100
    # - Add table
    # v0.0300
    # - Add selector for heart note and base note
    # - Add link
    # v0.0400
    # - Add axis conversion for heatmap
    # v0.0500
    # - Heatmap button
    # v0.0501
    # - Dashboard stuck if enable two callbacks
    # v0.0600
    # - Optimize layout
    
    
    # Worklist
    # - https://aronhack.pythonanywhere.com/
    # - Evolve, add Adsense to dash
    #   https://community.plotly.com/t/how-do-i-add-adsense-snippet-to-dash-app/29699
    # - Evolve, daily backup for google sheet 
    # - Evolve, iframe and scrollbar issue
    #   https://stackoverflow.com/questions/10082155/remove-scrollbar-from-iframe
    #   https://www.benmarshall.me/responsive-iframes/
    # - Optimize, translation
    # - Optimize, filter the option of dropdown when selectiong others
    pass
    
    

if __name__ == '__main__':
    
    app.run_server()
    # app.run_server(debug=True)



