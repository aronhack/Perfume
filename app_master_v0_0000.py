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
dev = False
dev = True


# import arsenal as ar
import codebase_yz as cbyz


# 自動設定區 -------
pd.set_option('display.max_columns', 30)



def init_path(host=2):

    global _host
    _host = host
    
    if _host == 2:
        path = r'/Users/Aron/Documents/GitHub/Perfume'
    elif _host == 4:
        path = r'D:\GitHub\Perfume'
        
    
    # Codebase
    path_codebase = ['/Users/Aron/Documents/GitHub/Arsenal',
                     '/Users/Aron/Documents/GitHub/Codebase_YZ',
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
    
    global data_raw, perfume, note, unique_note
    unique_note = []




def load_data():
    
    
    
    global data_raw, perfume, note, unique_note
    
    # Worklist
    # - Add affiliate link


    note_cols = ['top_note', 'heart_note', 'base_note']
    
    data_raw = pd.read_excel(path_resource + '/Perfume.xlsx')
    data_raw = data_raw.dropna(subset=['id'])
    data_raw = cbyz.df_conv_col_type(df=data_raw, cols='id', to='int')
    
    # Drop Columns
    cols = list(data_raw.columns)
    drop_cols = [c for c in cols if 'Unnamed' in c]
    data_raw = data_raw.drop(drop_cols, axis=1)


    # Replace special character as comma .....
    # Update, add df_replace_special for Chinese characters
    # data_raw = cbyz.df_replace_special(df=data_raw, cols=note_cols, value=',')
    # - Update，排處理「薑、肉荳蔻；」的符號
    
    for i in range(len(note_cols)):
        cur_col = note_cols[i]
        data_raw[cur_col] = data_raw[cur_col].str.replace('、', ',')
        data_raw[cur_col] = data_raw[cur_col].str.replace('.', ',')
        # data_raw[cur_col] = data_raw[cur_col].str.replace('；', ',')
        
        
        
        # Check「和」
        chk = data_raw[['id', cur_col]]
        chk = chk[chk[cur_col].str.contains('和')]

        if len(chk) > 0:
           print(chk) 
            
           
    perfume = data_raw[['id', 'brand', 'series', 'name', 'type']]
        

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


    unique_note = note['note'].unique().tolist()



    # Inspect
    chk_size = note \
                .groupby(['note']) \
                .size() \
                .reset_index(name='count')

    chk_size = chk_size \
                .sort_values(by=['count'], ascending=False) \
                .reset_index(drop=True)
                


def master(host=2):
    '''
    主工作區
    '''
    
    init()
    init_path(host=host)
    load_data()


