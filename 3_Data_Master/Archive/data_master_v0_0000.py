#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""


# % 讀取套件 -------
import pandas as pd
import numpy as np
import sys, time, os, gc
import time
import random
import shutil


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


host = 4
host = 0
shopee = 'https://shopee.tw/'


# Path .....
if host == 0:
    path = r'/Users/aron/Documents/GitHub/Perfume/3_Data_Master'
    path_nlp = r'/Users/aron/Documents/GitHub/Perfume/2_NLP'
    path_crawler = r'/Users/aron/Documents/GitHub/Perfume/1_Crawler'
elif host == 1:
    path = '/home/aronhack/stock_forecast/dashboard'
elif host == 4:
    path = r'D:\GitHub\Perfume\1_Crawler'

# Codebase ......
path_codebase = [r'/Users/aron/Documents/GitHub/Arsenal/',
                 r'/Users/aron/Documents/GitHub/Codebase',
                 r'D:\GitHub\Arsenal',
                 path_crawler + '/Function']


for i in path_codebase:    
    if i not in sys.path:
        sys.path = [i] + sys.path


import codebase_yz as cbyz
import arsenal as ar
import crawler_arsenal as crar


# 自動設定區 -------
path_resource = path + '/Resource'
path_function = path + '/Function'
path_temp = path + '/Temp'
path_export = path + '/Export'


cbyz.os_create_folder(path=[path_resource, path_function, 
                         path_temp, path_export])     

pd.set_option('display.max_columns', 30)
 




def master():
    
    
    # v0.0000
    # - Beginning
    # v1.0000
    # - Rewrite successfule rows of NER to a seperate sheet

    # Sheet Data
    url = 'https://docs.google.com/spreadsheets/d/19LhV8lWlXv53yGr3UWg5M3GJMHfE8lVPoxvy_K8rt9U/edit?usp=sharing'
    sheet_raw = ar.gsheets_get_sheet_data(url, worksheet='Perfume Manually')
    sheet_raw['title'] = np.nan
    sheet = sheet_raw[['brand', 'name', 'type', 'gender', 'link',
                       'top_note', 'heart_note', 'base_note']]
    
    sheet['top_note'] = sheet['top_note'].apply(cbyz.str_conv_half_width)
    sheet['heart_note'] = sheet['heart_note'].apply(cbyz.str_conv_half_width)
    sheet['base_note'] = sheet['base_note'].apply(cbyz.str_conv_half_width)

    sheet['top_note'] = sheet['top_note'].str.replace(' ', '')
    sheet['heart_note'] = sheet['heart_note'].str.replace(' ', '')
    sheet['base_note'] = sheet['base_note'].str.replace(' ', '')
    
    sheet = sheet \
        .rename(columns={'type':'type_sheet',
                         'gender':'gender_sheet'})
    sheet['priority'] = 0

    
    # Note ......
    path_note = path_crawler + '/Export'
    path_note = cbyz.os_get_dir_list(path=path_note, level=0,
                                     extensions='csv', contains='master_note')
    path_note = path_note['FILES']
    
    # Loop
    note = pd.DataFrame()
    
    for i in range(len(path_note)):
        new_df = pd.read_csv(path_note.loc[i, 'PATH'])
        note = note.append(new_df)

    note = note.dropna(subset=['title'])
    note = note[note['title']!='']
    
    # Bug
    note = note[~note['top_note'].str.contains('蝦皮購物')]


    # NER ......
    path_ner = path_nlp + '/Export'
    path_ner = cbyz.os_get_dir_list(path=path_ner, level=0,
                                     extensions='xlsx', contains='ner_master')
    path_ner = path_ner['FILES']
    ner = pd.DataFrame()

    for i in range(len(path_ner)):
        new_df = pd.read_excel(path_ner.loc[i, 'PATH'])
        ner = ner.append(new_df)        


    ner = ner.dropna(subset=['title'])
    ner = ner[ner['title']!='']
    ner = ner[['title', 'brand', 'name', 'name_en']]


    # Combine
    main_df = ner.merge(note, on='title')
    main_df = main_df[['title', 'brand', 'name', 'link',
                       'top_note', 'heart_note', 'base_note']]
    
    main_df = main_df[~main_df['name'].isna()]
    main_df['priority'] = 1    

    # Update, 移到crawler > function中
    main_df = crar.filter_type(df=main_df, 
                               string=['淡香水', '香水', '淡香精', '香精', '古龍水'],
                               value=['淡香水', '香水', '淡香精', '香精', '古龍水'],
                               backtrack=[False, True, False, True, False],
                               col='type',
                               source='title')
    
    main_df = crar.filter_type(main_df, 
                               string=['男', '女', '中性'],
                               value=['男性', '女性', '中性'],
                               col='gender')
    
    main_df = main_df.append(sheet)
    
    
    print('Optimize this with character set')
    main_df['top_note'] = main_df['top_note'].str.replace('前調:', '')
    main_df['top_note'] = main_df['top_note'].str.replace('前味:', '')
    main_df['heart_note'] = main_df['heart_note'].str.replace('中調:', '')
    main_df['heart_note'] = main_df['heart_note'].str.replace('中味:', '')
    main_df['base_note'] = main_df['base_note'].str.replace('後調:', '')
    main_df['base_note'] = main_df['base_note'].str.replace('後味:', '')
    
    
    
    main_df['gender'] = np.where(main_df['gender'].isna(),
                                 main_df['gender_sheet'],
                                 main_df['gender'])

    main_df['type'] = np.where(main_df['type'].isna(),
                                 main_df['type_sheet'],
                                 main_df['type'])


    print('Optimize - there are emoji in the note')

    main_df = main_df \
        .dropna(subset=['name', 'gender', 'type'], axis=0) \
        .sort_values(by=['name', 'priority']) \
        .drop_duplicates(subset=['brand', 'name'])        .reset_index(drop=True)

    main_df['name'] = main_df['name'] + main_df['gender'] + main_df['type']
    main_df = main_df[['brand', 'name', 'gender', 'type', 'link',
                       'top_note', 'heart_note', 'base_note']]

    ar.gsheets_sheet_write(data=main_df, url=url, worksheet='Perfume', 
                           start_col='A', start_row=1, 
                           append=False)


    print('Bug - title中的已售出數字會讓title對不上')
    print('Optimize - prevent 試香 or 小香')


if __name__ == '__main__':
    
    master()

