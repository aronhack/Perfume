# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 10:20:46 2022

@author: 吳雅智 Aron Wu
"""

# % 讀取套件 -------

import pandas as pd
import numpy as np
import sys, time, os, gc


# 設定工作目錄 .....
path = r'D:\GitHub\Perfume'
# path = r'/home/rserver/Data_Mining'


# Codebase
path_codebase = [path + '/Function',
                 'D:/Data_Mining/Projects/Codebase_YZ']

for i in path_codebase:    
    if i not in sys.path:
        sys.path = [i] + sys.path

    
import codebase_yz as cbyz
import codebase_rt as cbrt
import codebase_mk as cbmk
import toolbox as t
import codebase_ml as cbml



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




def master():
    
    
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
    for i in range(len(note_cols)):
        cur_col = note_cols[i]
        data_raw[cur_col] = data_raw[cur_col].str.replace('、', ',')
        data_raw[cur_col] = data_raw[cur_col].str.replace('.', ',')
        
        
        # Check「和」
        chk = data_raw[['id', cur_col]]
        chk = chk[chk[cur_col].str.contains('和')]

        if len(chk) > 0:
           print(chk) 
            
        

    # Parse Note ......
    note_raw = data_raw[['id'] + note_cols]
    note = pd.DataFrame()

    for i in range(len(note_cols)):
        
        cur_col = note_cols[i]
        new_data = cbyz.df_str_split(df=note_raw, col=cur_col,
                                     id_key='id', pat=',')    

        new_data.columns = ['id', 'note']
        new_data['type'] = cur_col
        note = note.append(new_data)


    note = note.reset_index(drop=True)
        
    
    
    # Level 1. Search Note 
    # - Y:Price / X:heart note 
    # - X:heart note / Y:base note
        
    len(note['note'].unique())




if __name__ == '__main__':
    master()













