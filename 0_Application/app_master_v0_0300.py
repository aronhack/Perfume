#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 23:09:54 2021

@author: Aron
"""


import os
import pandas as pd
import numpy as np
import sys
import datetime
import dash
import h5py


# 設定工作目錄 .....


# import arsenal as ar
import codebase_yz as cbyz
import arsenal as ar


# 自動設定區 -------
pd.set_option('display.max_columns', 30)



def init_path(host=2):

    global _host
    _host = host
    
    if _host==0:
        path = r'/Users/aron/Documents/GitHub/Perfume'
    elif _host == 1:
        path = r'/home/aronhack/perfume'
    elif _host == 4:
        path = r'D:\GitHub\Perfume'
        
    ar.host = _host
        
    
    # Codebase
    path_codebase = ['/Users/Aron/Documents/GitHub/Arsenal',
                     '/Users/Aron/Documents/GitHub/Codebase',
                     path, 
                     path + '/Function']

    # 新增工作資料夾
    global path_resource, path_function, path_temp, path_export
    path_resource = path + '/Resource'
    path_function = path + '/Function'
    path_temp = path + '/Temp'
    path_export = path + '/Export'
    
    
    cbyz.os_create_folder(path=[path_resource, path_function, 
                                path_temp, path_export])      
    
    for i in path_codebase:    
        if i not in sys.path:
            sys.path = [i] + sys.path
        


def init():
    
    global data_raw, perfume, note
    global unique_brand, unique_top_note, unique_heart_note, unique_base_note
    global unique_gender, unique_type
    
    unique_brand = []
    unique_top_note = []
    unique_heart_note = []
    unique_base_note = []
    
    unique_gender = []
    unique_type = []



def load_data():
    
    global data_raw, perfume, note, unique_note
    global unique_brand, unique_top_note, unique_heart_note, unique_base_note    
    global unique_gender, unique_type
    
    # Worklist
    # - Add affiliate link

    note_cols = ['top_note', 'heart_note', 'base_note']
    
    url = 'https://docs.google.com/spreadsheets/d/19LhV8lWlXv53yGr3UWg5M3GJMHfE8lVPoxvy_K8rt9U/edit?usp=sharing'
    data_raw = ar.gsheets_get_sheet_data(url, worksheet='Perfume')
    data_raw = cbyz.df_col_lower(df=data_raw)
    
    data_raw['id'] = data_raw.index
    data_raw = cbyz.df_conv_col_type(df=data_raw, cols='id', to='int')
    
    # Drop Columns
    cols = list(data_raw.columns)
    drop_cols = [c for c in cols if 'Unnamed' in c]
    data_raw = data_raw.drop(drop_cols, axis=1)


    # Replace old link
    if 'link2' in data_raw.columns:
        data_raw['link'] = np.where(data_raw['link2']!='',
                                    data_raw['link2'],
                                    data_raw['link'])
        
        data_raw = data_raw.drop('link', axis=1)


    # Replace special character as comma .....
    # Update, add df_replace_special for Chinese characters
    # data_raw = cbyz.df_replace_special(df=data_raw, cols=note_cols, value=',')
    # - Update，排處理「薑、肉荳蔻；」的符號
    
    print('Bug - note_prefix沒辦法完全排除，且str_conv_half_width會出錯')
    for i in range(len(note_cols)):
        
        cur_col = note_cols[i]
        data_raw[cur_col] = data_raw[cur_col].str.replace(' ', '')      
        
        data_raw[cur_col] = data_raw[cur_col].apply(cbyz.str_conv_half_width)
        
        
        if i == 0:
            note_prefix = ['前味:', '前味：', '前調:', '前調：']
        elif i == 1:
            note_prefix = ['中味:', '中味：', '中味：', '中調:', '中調：']
        elif i == 2:
            note_prefix = ['後味:', '後味：', '後調:', '後調：']
            
            
        for n in note_prefix:    
            data_raw[cur_col] = data_raw[cur_col].str.replace(n, '')        
        
        
        data_raw[cur_col] = data_raw[cur_col].str.replace('、', ',')
        data_raw[cur_col] = data_raw[cur_col].str.replace('.', ',')

        
        # data_raw[cur_col] = data_raw[cur_col].str.replace('；', ',')
        
        # Check「和」
        chk = data_raw[['id', cur_col]]
        chk = chk.dropna(axis=0)
        chk = chk[chk[cur_col].str.contains('和')]

        if len(chk) > 0:
           print(chk) 
            
           
    perfume = data_raw[['id', 'brand', 'name', 'type']]
        

    # Parse Note ......
    note_raw = data_raw[['id'] + note_cols]
    note = pd.DataFrame()

    for i in range(len(note_cols)):
        
        cur_col = note_cols[i]
        new_data = cbyz.df_str_split(df=note_raw, col=cur_col,
                                     id_key='id', pat=',')    

        new_data.columns = ['id', 'note']
        new_data['note_type'] = cur_col
        note = note.append(new_data)



    # Unique
    unique_brand = perfume['brand'].unique().tolist()

    unique_top_note = note[note['note_type']=='top_note']
    unique_top_note = unique_top_note['note'].unique().tolist()
    
    unique_heart_note = note[note['note_type']=='heart_note']
    unique_heart_note = unique_heart_note['note'].unique().tolist()
    
    unique_base_note = note[note['note_type']=='base_note']
    unique_base_note = unique_base_note['note'].unique().tolist()

    unique_gender = data_raw['gender'].unique().tolist()
    unique_type = data_raw['type'].unique().tolist()
    
    
    # Inspect
    # chk_size = note \
    #             .groupby(['note']) \
    #             .size() \
    #             .reset_index(name='count')

    # chk_size = chk_size \
    #             .sort_values(by=['count'], ascending=False) \
    #             .reset_index(drop=True)
                


def master(host=2):
    '''
    主工作區
    '''
    
    # v0.0300    
    # - 讓前調selector中只有前調的note
    
    init()
    init_path(host=host)
    load_data()


