#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 20:22:13 2019

@author: Aron
"""


import selenium
shopee_url = 'https://shopee.tw/'

from selenium import webdriver

driver = webdriver.Chrome('/path/to/chromedriver')


# driver = webdriver.Chrome()
# driver.get(shopee_url)


# q = driver.find_element_by_class_name('shopee-searchbar-input__input')
# q.send_keys('後背包')
#
# from selenium.webdriver.common.keys import Keys
# q.send_keys(Keys.RETURN)
#
# from bs4 import BeautifulSoup
# soup = BeautifulSoup(driver.page_source,'lxml')
#
# print(soup)

# links = soup.find_all(class_="shopee-search-item-result__item")
#links = soup.find_all('div', class_= ['shopee-search-item-result__item', 'col-xs-2-4'])
#print(len(links))
# print(links)


#for link in links:
#     print(link['href'])
#     print(link.text)
#     print(shopee_url+items[4]['href'])

#    driver.get(shopee_url+link['href'])
#    soup_lv2 = BeautifulSoup(driver.page_source,'lxml')
#    selling_data = soup_lv2.find_all("div", "shopee-product-info__header__sold-count")
#    print(selling_data)
    
    
#     count = soup.find_all('div', class_= 'shopee-product-info__header__sold-count')
#     print(count.text)


#     driver.get(shopee_url+links[4]['href'])

#     print(len(soup_lv2.find_all("div")))

#     for data in selling_data:
#         print(data.text)
    