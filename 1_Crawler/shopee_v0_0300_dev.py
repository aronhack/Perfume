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


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


host = 4
# host = 0
shopee = 'https://shopee.tw/'


# Path .....
if host == 0:
    path = r'/Users/aron/Documents/GitHub/Perfume/1_Crawler'
elif host == 1:
    path = '/home/aronhack/stock_forecast/dashboard'
elif host == 4:
    path = r'D:\GitHub\Perfume\1_Crawler'

# Codebase ......
path_codebase = [r'/Users/aron/Documents/GitHub/Arsenal/',
                 r'/Users/aron/Documents/GitHub/Codebase_YZ',
                 r'D:\GitHub\Arsenal']


for i in path_codebase:    
    if i not in sys.path:
        sys.path = [i] + sys.path


import codebase_yz as cbyz
import arsenal as ar
import arsenal_stock as stk



# 自動設定區 -------
path_resource = path + '/Resource'
path_function = path + '/Function'
path_temp = path + '/Temp'
path_export = path + '/Export'


cbyz.os_create_folder(path=[path_resource, path_function, 
                         path_temp, path_export])     

pd.set_option('display.max_columns', 30)
 



def crawl_search_result(driver, term):
    
    term_brand = ''
    if ' 香水' in term:
        term_brand = term.replace(' 香水', '')
    
    # Search
    query = driver.find_element_by_class_name('shopee-searchbar-input__input')
    query.clear()
    query.send_keys(term)
    query.send_keys(Keys.RETURN)


    # Page Controller
    # - First page link: https://shopee.tw/[search_term]?page=0
    term_url = driver.current_url
    
    
    # Page Controller
    # - page=0 is the firest page
    global item_link
    item_link = []
    
    
    print('Update, split item name by $ mark')
    
    for p in range(10):
    # for p in range(2000):

        if p == 0:
            page_url = term_url
        elif p > 0:
            page_url = term_url + '&page=' + str(p)
            driver.get(page_url)
            
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
            
        # Prevent errors by lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
    
        # Page number too huge ...
        # page_url = 'https://shopee.tw/search?keyword=coach&page=2000'
        # - 找不到結果 / 我們找不到 coachpage 商品 顯示 'coach bag'的搜尋結果。
        empty = soup.select('.shopee-search-empty-result-section__title')
        if len(empty) > 0:
            pass
            break
        
        # Search result is empty
        # page_url = 'https://shopee.tw/search?keyword=coachpage'
        # - 我們找不到
        empty = soup.select('.shopee-search-result-header__text')
        if len(empty) > 0 and '我們找不到' in empty[0].text:
            pass
            break     

        links = soup.find_all(class_='shopee-search-item-result__item')
        new_link = []
    
        # Query Item Info
        for i in range(len(links)):
            link = links[i]
            link = link.findChildren('a', recursive=False)
            
            if len(link) > 0:
                link = link[0]
            else:
                continue
    
            new_link.append([link.text, link['href']])
        
            
        item_link = item_link + new_link
        print('page ', p, ' has ', len(new_link), ' items.')
        time.sleep(random.randint(2, 5))
        
    
    if len(item_link) > 0:
        item_df = pd.DataFrame(item_link, columns=['title', 'link'])
        item_df['link'] = shopee + item_df['link']
        item_df['search_term'] = term_brand
        
        serial = cbyz.get_time_serial(with_time=True)
        item_df.to_csv(path_export + '/item_df_' + serial + '.csv',
                       index=False, encoding='utf-8-sig')
    
    
    
# %% File Management ------
        
def combine_file():

    serial = cbyz.get_time_serial(with_time=True)
    files = cbyz.os_get_dir_list(path=path_export, level=-1, 
                                 extensions=['csv'], remove_temp=True)
    
    files = files['FILES']
    loc_df = pd.DataFrame()

    for i in range(len(files)):
        
        file = files.loc[i, 'PATH']
        file_serial = file[-19:-4]
        cur_file = pd.read_csv(file)
        cur_file['serial'] = file_serial
        loc_df = loc_df.append(cur_file)
        
    if len(loc_df) == 0:
        return

    loc_df = loc_df[~loc_df['title'].str.contains('廣告')]


    data = pd.read_excel(path_resource + '/data.xlsx')
    
    # Backup
    data.to_excel(path_resource + '/Backup/data_' + serial + '.xlsx',
                  index=False, encoding='utf-8-sig')    
    
    data = data.append(loc_df)
    
    
    # Fill Brand
    brand = data[['serial', 'search_term']]
    brand = brand.dropna(axis=0)
    
    data = data.drop('brand', axis=1)
    data = data.merge(brand, how='left', on='serial')
    
    # Ensure brand or synonym in name 
    # data['brand'] = np.where(data['brand'].isin(data['name']))
    # df.apply(lambda x: x.A in x.B, axis=1)
    

    # Export
    data.to_excel(path_resource + '/data.xlsx',
                  index=False, encoding='utf-8-sig')
    
    
def create_dict():
    
    dict_df = pd.read_excel(path_resource + '/dict.xlsx')
    
    serial = cbyz.get_time_serial(with_time=True)
    dict_df.to_excel(path_resource + '/Backup/dict_' + serial + '.xlsx',
                     index=False, encoding='utf-8-sig')    
    
    # Brand
    data = pd.read_excel(path_resource + '/data.xlsx')
    brand = data[['brand']].drop_duplicates()
    brand.columns = ['word']

    # Synonym
    synonym = pd.read_excel(path_resource + '/synonym.xlsx')
    synonym = synonym.melt()
    synonym = synonym[['value']]
    synonym.columns = ['word']
    
    
    dict_df = dict_df.append(brand).append(synonym)
    dict_df = dict_df.drop_duplicates().reset_index(drop=True)
    

    dict_df.to_excel(path_resource + '/dict.xlsx', 
                     index=False, encoding='utf-8-sig')

    
    return    
    
    


# %% Execute ------


def master():
    
    # Simulate human behaviors
    # https://www.selenium.dev/documentation/webdriver/actions_api/mouse/
    # https://stackoverflow.com/questions/51340300/simulate-mouse-movements-in-selenium-using-python
    
    
    # v0.0200
    # - Add NLP function

    # v0.0300
    # - Remove rows with 廣告
    
    
    
    url = 'https://docs.google.com/spreadsheets/d/19LhV8lWlXv53yGr3UWg5M3GJMHfE8lVPoxvy_K8rt9U/edit?usp=sharing'
    terms = ar.gsheets_get_sheet_data(url, worksheet='Term')
    
    print('Should handle url encoding issues. Refer to automation > weather')
    
    
    driver = webdriver.Firefox(executable_path=path + '/geckodriver')
    driver.get(shopee)
    
    
    for i in range(len(terms)):
        term = terms.loc[i, 'term']
        term = term + ' 香水'
        
        # url encoding
        # term = term.replace(' ', '%20')
        crawl_search_result(driver, term)
        
    driver.close()



if __name__ == '__main__':
    
    master()

