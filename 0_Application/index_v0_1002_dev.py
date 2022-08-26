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
# host = 4
# host = 0


if host == 0:
    path = r'/Users/aron/Documents/GitHub/Perfume/0_Application'
elif host == 1:
    path = r'/home/aronhack/perfume'
elif host == 4:
    path = r'D:\GitHub\Perfume\0_Application'


# Codebase
path_codebase = [path, 
                 path + '/Function',
                 r'/Users/aron/Documents/GitHub/Arsenal/',
                 r'/Users/aron/Documents/GitHub/Codebase',
                 r'D:/Data_Mining/Projects/Codebase',
                 r'D:\GitHub\Arsenal']

for i in path_codebase:    
    if i not in sys.path:
        sys.path = [i] + sys.path

    
import codebase_yz as cbyz
# import codebase_ml as cbml


import app_master_v0_0300 as ms
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

def dashboard(gender=[], perfume_type=[], brand=[], name=[], 
              top_note=[], heart_note=[], base_note=[], status=0):
    
    
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
    # gender = ['女性']
    
    # top_note = []
    # heart_note = []
    # base_note = []
    
    gender = cbyz.conv_to_list(gender)
    perfume_type = cbyz.conv_to_list(perfume_type)
    
    brand = cbyz.conv_to_list(brand)
    name = cbyz.conv_to_list(name)
    
    top_note = cbyz.conv_to_list(top_note)
    heart_note = cbyz.conv_to_list(heart_note)
    base_note = cbyz.conv_to_list(base_note)


    # 全部的note取交集
    target_id_df = ms.note.copy()
    
    
    loop_key = [gender, perfume_type, brand]
    cols = ['gender', 'type', 'brand']
    
    for i in range(len(loop_key)):
        key = loop_key[i]
        
        if len(key) > 0:
            merge_item = ms.data_raw[ms.data_raw[cols[i]].isin(key)]
            merge_item = merge_item[['id']].drop_duplicates()
            target_id_df = target_id_df.merge(merge_item, on='id')    
        
    if len(name) > 0:
        name = '|'.join(name)
        item_name = ms.perfume[ms.perfume['name'].str.contains(name)]
        item_name = item_name[['id']].drop_duplicates()
        target_id_df = target_id_df.merge(item_name, on='id')
        
    
    
    note_li = [top_note, heart_note, base_note]
    note_str_li = ['top_note', 'heart_note', 'base_note']
    
    
    for i in range(3):
        
        cur_note = note_li[i]
        cur_note_str = note_str_li[i]
        if len(cur_note) > 0:
            inner_id = \
                target_id_df[(target_id_df['note'].isin(cur_note)) \
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
    
    print('Optimize - move this to app_master')
    perfume_list['name'] = '[' + perfume_list['name'] + '](' \
                            + perfume_list['link'] + ')'    
    
    perfume_list = perfume_list[['gender', 'type', 'brand', 'name',
                                 'top_note', 'heart_note', 'base_note']]
    
    perfume_list.columns = ['性別', '類型', '品牌', '名稱', 
                            '前調', '中調', '後調']
    
    
    cols = [{"name": i, "id": i} for i in perfume_list.columns]
    cols[3]['presentation'] = 'markdown'

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
            xaxis={'title':x_note, 'fixedrange':True},
            yaxis={'title':y_note, 'fixedrange':True},
            height=500
        ) 


    heatmap = go.Figure(data=go.Heatmap(z=heatmap_data,
                                        x=x_label, y=y_label, hoverongaps=False,
                                        colorscale=colors),
                        layout=layout)
    
    return heatmap_data, heatmap



# %% Layout ----

note_selector_css = {
    # 'width': '50%', 
    'padding-top': '15px', 
    'display': 'block',
    }

print('Evolve, fix table layout as width by 100%')
table_css = {
    'width': '100%',
    # 'margin-left': '5%',
    # 'margin-right': '5%' 
    }

footer_style = {
    'font-size':'14px',
    'text-align':'center',
    'margin':'12px 0',
    }



# %% Application ----

# Iniitialize ......
external_stylesheets = [dbc.themes.BOOTSTRAP]


app = Dash(meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            ],
            external_stylesheets=external_stylesheets)
ms.master(host)


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

tb_data, tb_cols, init_heatmap_data, init_heatmap = dashboard()
ah_logo = r'https://aronhack.com/wp-content/themes/aronhack/assets/header/logo_v2_wide.png'

# app.scripts.append_script({
#     "external_url": my_js_url
# }) 


# <!-- AdSense AMP Auto Ad -->
# <script async custom-element="amp-auto-ads"
#         src="https://cdn.ampproject.org/v0/amp-auto-ads-0.1.js">
# </script>



# https://stackoverflow.com/questions/61305223/how-to-add-google-analytics-gtag-to-my-python-dash-app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <!-- Google AdSense -->
        <script data-ad-client="ca-pub-3866010510626398" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        

        {%metas%}
        <title>調香秘策 – 知名品牌香水調性分析與搭配</title>
        {%favicon%}
        {%css%}
    </head>
    <body>

        <div align="center">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3866010510626398"
                 crossorigin="anonymous"></script>
            <!-- Perfume Dashboard Header Ad -->
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-3866010510626398"
                 data-ad-slot="2109170626"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>        
        </div>

        {%app_entry%}

        <div align="center">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3866010510626398"
                 crossorigin="anonymous"></script>
            <!-- Perfume Footer Ad -->
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-3866010510626398"
                 data-ad-slot="3745422594"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>     
        </div>


        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''



app.layout = html.Div([
    
    html.Div( 
    html.Div([
        html.Div(html.A(html.Img(src=ah_logo,
                                 style={'width':'110px'},
                                 className='my-4 ',),
                        href='https://perfume.aronhack.com/',
                        ),
                 className='col-6'
                 ),
        
        html.Div(html.Nav([html.A('首頁', 
                                  className="nav-item nav-link text-dark",
                                  href='https://aronhack.com/zh/home-zh/'),
                           html.A('說明', 
                                  className="nav-item nav-link text-dark", 
                                  href='https://aronhack.com/zh/the-secrets-of-perfume-making-guide-zh/')
                           ],
                          className = 'nav nav-pills ', 
            ),
            className='col-6',
            style={'justify-content':'right',
                   'align-items':'center',
                   'display': 'flex'},
            ),
        ],
        className='row'
        ),
    className=''
    ),
    
    html.H1('調香秘策 – 知名品牌香水調性分析與搭配',
            style={'font-size':'1.8em',
                   'margin':'30px 0'}),

    
    dcc.Location(id='url', refresh=False),
    html.Div(id='debug'),
    
    # Settings
    dcc.Input(id="device", type='hidden', value=0),    
    # dcc.Input(id="tick0", type='hidden', value=ms.first_date_lite),    
    dcc.Input(id="dtick", type='hidden', value=20),


    dbc.Row([

        
        dbc.Col(
            html.Div([
                html.Label('性別'),
                dcc.Dropdown(
                    id='gender_selector',
                    options=ms.unique_gender,
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
                html.Label('類型'),
                dcc.Dropdown(
                    id='type_selector',
                    options=ms.unique_type,
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
                html.Label('品牌'),
                dcc.Dropdown(
                    id='brand_selector',
                    options=ms.unique_brand,
                    multi=True,
                    value=[]
                        ),
                    ], 
                style=note_selector_css
                ),
            width=12,
            md=4
            ),
        
        # dbc.Col(
        #     html.Div([
        #         html.Label('名稱'),
        #         dcc.Dropdown(
        #             id='name',
        #             options=ms.unique_brand,
        #             multi=True,
        #             value=[]
        #                 ),
        #             ], 
        #         style=note_selector_css
        #         ),
        #     width=12,
        #     md=4
        #     ),        
        ]), 


    dbc.Row([

        dbc.Col(
            html.Div([
                html.Label('前調'),
                dcc.Dropdown(
                    id='top_note_selector',
                    options=ms.unique_top_note,
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
                    options=ms.unique_heart_note,
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
                    options=ms.unique_base_note,
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
        className='mb-4',
    ),

    html.Div([dash_table.DataTable(
                id='perfume_list',
                data=tb_data,
                columns=tb_cols,
                page_size=6,
                style_cell={'textAlign': 'left'},
                ),    
            ], 
        style=table_css,
        # className='text-left'
        ),

    dcc.Input(id="heatmap_status", type='hidden', value=0),        
    html.Button('切換', id='heatpmap_convert', n_clicks=0),
    
    dcc.Store(id='heatmap_data'),
    dcc.Graph(id="graph", figure=init_heatmap, 
              config={'displayModeBar': False}),
    
    html.Div([html.Span(['Powered by ',
                        html.A('PythonAnywhere', 
                               href='https://aronhack.studio/pythonanywhere_dash',
                               target='_blank',
                               className='text-decoration-none')
                        ]),
              html.Span(' - Created by Angel & Aron'),
              html.Span(['© 2022 ',
                        html.A('ARON HACK 亞倫害的.', 
                               href='https://aronhack.studio/aronhack_dash_footer',
                               target='_blank',
                               className='text-decoration-none'),
                        ' All Rights Reserved'],
                        className='d-block'),
             ],
             style=footer_style
             ),
    
    
    ],
    className='p-4',
)



# %% Callback ----

@app.callback(
    # Output('debug', 'value'),
    Output('perfume_list', 'data'),
    Output('heatmap_status', 'value'),
    # Output('heatmap_data', 'data'),
    Output('graph', 'figure'),
    Input('gender_selector', 'value'),
    Input('type_selector', 'value'),
    Input('brand_selector', 'value'),
    # Input('name', 'value'),
    Input('top_note_selector', 'value'),
    Input('heart_note_selector', 'value'),
    Input('base_note_selector', 'value'),
    Input('heatpmap_convert', 'n_clicks'),
    State('heatmap_status', 'value')
)

def update_note(gender, perfume_type, brand, top_note, heart_note, base_note, 
                clicks, status):

    
    if status == 2:
        status = 0
    else:
        status = status + 1


    tb_data, tb_cols, heatmap_data, heatmap = \
        dashboard(gender, perfume_type, brand, [], 
                  top_note, heart_note, base_note, status)

    
    return tb_data, status, heatmap
    


# %% Debug ------

def debug():
    
    debug_df =  ms.data_raw.copy()
    debug_df = debug_df[debug_df['top_note'].str.contains('佛手柑')]
    
    pass


# %% Execute ------
    

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
    # v0.0602
    # - Remove blank in the note
    # - Remove id in the google sheet
    # v0.0603
    # - Update for new structure of google sheet
    # v0.0700
    # - Disable zoom
    # - Add brand dropdown
    # v0.0800
    # - Add gender
    # - Add shopee affiliate link
    # - Add PythonAnywhere affiliate link
    # - Add all rights reserved text
    # - Give up to add X-Frame-Options, but add affiliate link to the footer 
    #   of dashboards.    
    # v0.0900
    # - To redirect website to application
    # v0.1000
    # - Add AdSense code
    

    # v0.1002
    # - 還沒想好這個版本要改什麼

    
    # Worklist
    # - Add name dropdown - Not yet   
    # - Fix upper case and lower case issues of brand
    # - Add line break for the note of table
    # - https://aronhack.pythonanywhere.com/
    # - 防盜機制, if all seslector are empty, then show nothing
    # - Add brand filter
    # - 香水名稱要有中文
    # - Evolve, add Adsense to dash
    #   https://community.plotly.com/t/how-do-i-add-adsense-snippet-to-dash-app/29699
    # - Evolve, daily backup for google sheet 
    # - Evolve, iframe and scrollbar issue
    #   https://stackoverflow.com/questions/10082155/remove-scrollbar-from-iframe
    #   https://www.benmarshall.me/responsive-iframes/
    # - Optimize, translation
    # - Optimize, filter the option of dropdown when selectiong others    
    
    
    
    # Item
    # [https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=3590798&Area=search&mdiv=403&oid=1_6&cid=index&kw=Atlantiqve 寶格麗勁藍水能量男性淡香水](https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=3590798&Area=search&mdiv=403&oid=1_6&cid=index&kw=Atlantiqve%20%E5%AF%B6%E6%A0%BC%E9%BA%97%E5%8B%81%E8%97%8D%E6%B0%B4%E8%83%BD%E9%87%8F%E7%94%B7%E6%80%A7%E6%B7%A1%E9%A6%99%E6%B0%B4#)
    # Affiliate
    # [http://www.momoshop.com.tw/goods/GoodsDetail.jsp?osm=league&i_code=3590798&cid=apuad&oid=1&memid=6000020207](http://www.momoshop.com.tw/goods/GoodsDetail.jsp?osm=league&i_code=3590798&cid=apuad&oid=1&memid=6000020207)
    # oid=1應該是直接用連結, 2是用sticker
    # cid都是apuad



    pass
    
    

if __name__ == '__main__':
    
    app.run_server()
    # app.run_server(debug=True)



