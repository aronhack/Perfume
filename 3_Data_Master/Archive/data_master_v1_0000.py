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
    
    
    # v2.0000
    # - affiliate link用銷售量最好的
    
    # - Add capitalize() function, and write a function to modify old data


    print('Bug - title中的已售出數字會讓title對不上')
    print('Optimize - prevent 試香 or 小香')
    


    # Sheet Data
    url = 'https://docs.google.com/spreadsheets/d/19LhV8lWlXv53yGr3UWg5M3GJMHfE8lVPoxvy_K8rt9U/edit?usp=sharing'
    # sheet_raw = ar.gsheets_get_sheet_data(url, worksheet='Perfume Manually')
    # sheet_raw['title'] = np.nan
    # sheet = sheet_raw[['brand', 'name', 'type', 'gender', 'link',
    #                    'top_note', 'heart_note', 'base_note']]
    
    # sheet['top_note'] = sheet['top_note'].apply(cbyz.str_conv_half_width)
    # sheet['heart_note'] = sheet['heart_note'].apply(cbyz.str_conv_half_width)
    # sheet['base_note'] = sheet['base_note'].apply(cbyz.str_conv_half_width)

    # sheet['top_note'] = sheet['top_note'].str.replace(' ', '')
    # sheet['heart_note'] = sheet['heart_note'].str.replace(' ', '')
    # sheet['base_note'] = sheet['base_note'].str.replace(' ', '')
    
    # sheet = sheet \
    #     .rename(columns={'type':'type_sheet',
    #                      'gender':'gender_sheet'})
    # sheet['priority'] = 0

    
    # Note ......
    path_note = path_crawler + '/Temp/Note'
    path_note = cbyz.os_get_dir_list(path=path_note, level=0,
                                     extensions='csv', contains='note_')
    path_note = path_note['FILES']
    
    # Loop
    note = pd.DataFrame()
    
    for i in range(len(path_note)):
        new_df = pd.read_csv(path_note.loc[i, 'PATH'])
        note = note.append(new_df)

    note = note.dropna(subset=['title'])
    note = note[note['title']!='']
    
    # Bug
    note['top_note'] = note['top_note'].astype('str')
    note = note[~note['top_note'].str.contains('蝦皮購物')]


    # NER ......
    path_ner = path_nlp + '/Export/'
    ner_done = pd.read_excel(path_ner + 'ner_done.xlsx')
    ner_remove = pd.read_excel(path_ner + 'ner_remove.xlsx')

    ner_pool = pd.read_excel(path_ner + 'ner_pool.xlsx')
    ner_pool = ner_pool.dropna(subset=['title'], axis=0)
    
    ner_pool.isnull().sum()
    
    ner = ner_done.append(ner_pool)
    ner = ner.dropna(subset=['title', 'link'])
    ner = ner[ner['title']!='']
    ner = ner[['link', 'title', 'brand', 'name', 'name_en']]


    # Combine
    main_df = ner.merge(note, on=['link', 'title'])
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
    
    # main_df = main_df.append(sheet)
    
    
    print('Optimize this with character set')
    main_df['top_note'] = main_df['top_note'].str.replace('前調:', '')
    main_df['top_note'] = main_df['top_note'].str.replace('前味:', '')
    main_df['heart_note'] = main_df['heart_note'].str.replace('中調:', '')
    main_df['heart_note'] = main_df['heart_note'].str.replace('中味:', '')
    main_df['base_note'] = main_df['base_note'].str.replace('後調:', '')
    main_df['base_note'] = main_df['base_note'].str.replace('後味:', '')
    
    
    # main_df['gender'] = np.where(main_df['gender'].isna(),
    #                              main_df['gender_sheet'],
    #                              main_df['gender'])

    # main_df['type'] = np.where(main_df['type'].isna(),
    #                              main_df['type_sheet'],
    #                              main_df['type'])


    print('Optimize - there are emoji in the note')

    main_df = main_df[main_df['name']!=''] \
        .dropna(subset=['name', 'gender', 'type'], axis=0) \
        .sort_values(by=['name', 'priority']) \
        .drop_duplicates(subset=['brand', 'name']) \
        .reset_index(drop=True)

    main_df['full_name'] = main_df['name'] + main_df['gender'] + main_df['type']
    main_df = main_df[['title', 'brand', 'name', 'gender', 'type', 'link',
                       'top_note', 'heart_note', 'base_note']]

    ar.gsheets_sheet_write(data=main_df, url=url, worksheet='Perfume', 
                           start_col='A', start_row=1, 
                           append=False)


    # Update NER Sheet ......
    title_done = main_df[['title', 'link']].dropna(axis=0)
    # title_done = main_df[['link']].dropna(axis=0)
    
    # Done ...
    ner_done_new = ner_pool.merge(title_done, on=['link', 'title'])
    ner_done = ner_done.append(ner_done_new)
    ner_done = ner_done \
        .dropna(subset=['name'], axis=0) \
        .drop_duplicates(subset='title')
    
    ner_done.to_excel(path_ner + 'ner_done.xlsx',
                      index=False, encoding='utf-8-sig')
    
    
    # Pool And Remove ...
    ner_pool = cbyz.df_anti_merge(ner_pool, title_done, on=['title', 'link'])
    
    main_unique = main_df[['brand', 'name']]
    unique_brand = ner_pool[['brand']].drop_duplicates().reset_index(drop=True)
    
    ner_remove_new = pd.DataFrame()
    ner_pool_new = pd.DataFrame()
    
    chk = 0
    
    for i in range(len(unique_brand)):
        
        cur_brand = unique_brand.loc[i, 'brand']
        loc_pool = ner_pool[ner_pool['brand']==cur_brand]
        
        chk = chk + len(loc_pool)
        
        loc_main_unique = \
            main_unique[main_unique['brand']==cur_brand]
        
        print('Bug - 男香和女香可能會有一樣的名字，像是同名經典，在這裡會出錯')
        loc_name = loc_main_unique['name'].tolist()
        
        # 排除名稱已完成的row
        if len(loc_name) > 0:
            regex = '|'.join(loc_name)
            pool_new = loc_pool[~loc_pool['title'].str.contains(regex)]
            remove_new = loc_pool[loc_pool['title'].str.contains(regex)]
        else:
            pool_new = loc_pool.copy()
            remove_new = loc_pool[loc_pool.index<0]
        
        ner_pool_new = ner_pool_new.append(pool_new)
        ner_remove_new = ner_remove_new.append(remove_new)
        
    # Oraganize
    ner_remove = ner_remove.append(ner_remove_new)
    ner_remove = ner_remove.drop_duplicates(subset='title')
    
    ner_pool_new = ner_pool_new.sort_values(by=['brand', 'name']) 
    ner_pool_new = ner_pool_new.dropna(subset=['link'], axis=0)
        
    # Export
    ner_remove.to_excel(path_ner + 'ner_remove.xlsx',
                        index=False, encoding='utf-8-sig')
    
    ner_pool_new.to_excel(path_ner + 'ner_pool.xlsx',
                          index=False, encoding='utf-8-sig') 
    
    print('Bug - 會出現完全相同，但是連結不一樣的資料')
# VERSACE BRIGHT CRYSTAL香戀水晶女用淡香水(5ml)【小三美日】空運禁送 D993871$250已售出 32彰化縣鹿港鎮找相似	Versace	香戀水晶	女性	淡香水	https://shopee.tw//VERSACE-BRIGHT-CRYSTAL香戀水晶女用淡香水(5ml)【小三美日】空運禁送-D993871-i.11527054.102797573?sp_atk=813e17ae-cd25-4c6a-bacc-74c2259fa13e&xptdk=813e17ae-cd25-4c6a-bacc-74c2259fa13e	石榴、柚子
# VERSACE 凡賽斯 香戀水晶 女性淡香水 30ml/50ml/90ml 《BEAULY倍莉》 情人節禮物 經典香水滿額折$180$990 - $1,950臺中市南區找相似	Versace	香戀水晶 	女性	淡香水	https://shopee.tw//VERSACE-凡賽斯-香戀水晶-女性淡香水-30ml-50ml-90ml-《BEAULY倍莉》-情人節禮物-經典香水-i.313807339.9660247984?sp_atk=7093d4db-c272-4a47-8cab-500e6de0d065&xptdk=7093d4db-c272-4a47-8cab-500e6de0d065	石榴、柚子    
    


def recycle_removed():

    ner_remove_file = '/Users/aron/Documents/GitHub/Perfume/2_NLP/Export/ner_remove.xlsx'
    ner_remove = pd.read_excel(ner_remove_file)
    
    ner_pool_file = '/Users/aron/Documents/GitHub/Perfume/2_NLP/Export/ner_pool.xlsx'
    ner_pool = pd.read_excel(ner_pool_file)
    
    ner_pool = ner_pool.append(ner_remove)
    ner_pool = ner_pool.sort_values(by=['brand', 'name'])     
    ner_pool.to_excel(ner_pool_file, index=False, encoding='utf-8-sig')

    ner_remove = ner_remove[ner_remove.index<0]
    ner_remove.to_excel(ner_remove_file, index=False, encoding='utf-8-sig')




def refill_link():

    item_file = '/Users/aron/Documents/GitHub/Perfume/1_Crawler/Temp/Archive'
    files = cbyz.os_get_dir_list(path=item_file, level=0, 
                                 extensions=['csv'], remove_temp=True)
    
    files = files['FILES']    
    link = pd.DataFrame()

    for i in range(len(files)):
        
        df = pd.read_csv(files.loc[i, 'PATH'])
        link = link.append(df)

    link = link[['title', 'link']]
    link.columns = ['title', 'link_2']


    ner_pool_file = '/Users/aron/Documents/GitHub/Perfume/2_NLP/Export/ner_pool.xlsx'
    ner_pool = pd.read_excel(ner_pool_file)
    ner_pool.isnull().sum()
    
    
    ner_pool = ner_pool.merge(link, how='left', on='title')
    ner_pool = ner_pool \
        .sort_values(by=['brand', 'link', 'name'], ascending=False) \
        .drop_duplicates()
        
    ner_pool['link'] = np.where(ner_pool['link'].isna(),
                                ner_pool['link_2'],
                                ner_pool['link'])
    
    ner_pool = ner_pool.drop('link_2', axis=1)
    ner_pool.to_excel(ner_pool_file, index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    
    master()

