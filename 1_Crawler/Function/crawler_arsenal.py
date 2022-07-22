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


import codebase_yz as cbyz



def filter_type(df, col, string, value, backtrack=[], source='title'):
    '''
    Keep rows with one type only
    '''
    
    assert isinstance(string, list), 'Error'
    assert len(string) == len(value), 'Error'
    assert len(string) == len(backtrack) or len(backtrack) == 0, 'Error'    
    
    
    loc_df_raw = df.copy()
    
    assert 'index' not in loc_df_raw.columns, 'Error'
    loc_df_raw = loc_df_raw.reset_index(drop=True)
    loc_df_raw['index'] = loc_df_raw.index    
    loc_df = loc_df_raw[['index', source]]
    
    type_li = [col + '_' + str(i) for i in range(len(string))]
    
    
    # 如果title是NA的話，會全部被標為1，但會在下面的count被排除，所以不影響
    for i in range(len(string)):
        cond_contains = loc_df[source].str.contains(string[i])
        
        # 避免「香水」覆寫「淡香水」
        if len(backtrack) > 0 and backtrack[i]:
            cond_contains = (cond_contains) & (loc_df[type_li[i-1]]==0)
        
        loc_df[type_li[i]] = np.where(cond_contains, 1, 0)

    loc_df = loc_df.melt(id_vars='index', var_name=col, value_vars=type_li)
    loc_df = loc_df[loc_df['value']==1]
    loc_df = cbyz.df_add_size(df=loc_df, group_by=['index'], col_name='count')
    loc_df = loc_df[loc_df['count']==1]
    loc_df = loc_df[['index', col]]
    
    cond = []
    for i in range(len(type_li)):
        cond.append(loc_df[col]==type_li[i])
        
    loc_df[col] = np.select(cond, value)
    result = loc_df_raw.merge(loc_df, how='left', on='index')
    result = result.drop('index', axis=1)
    
    return result



# def filter_type_20220722(df, col, string, value, source='title'):
#     '''
#     Keep rows with one type only
#     '''
    
#     print('Bug - string要考慮重疊的問題')
#     assert isinstance(string, list), 'Error'
#     loc_df_raw = df.copy()
    
#     assert 'index' not in loc_df_raw.columns, 'Error'
#     loc_df_raw = loc_df_raw.reset_index(drop=True)
#     loc_df_raw['index'] = loc_df_raw.index    
#     loc_df = loc_df_raw[['index', source]]
    
#     type_li = [col + '_' + str(i) for i in range(len(string))]
    
    
#     # 如果title是NA的話，會全部被標為1，但會在下面的count被排除，所以不影響
#     for i in range(len(string)):
#         loc_df[type_li[i]] = np.where(
#             loc_df[source].str.contains(string[i]), 1, 0)

#     loc_df = loc_df.melt(id_vars='index', var_name=col, value_vars=type_li)
#     loc_df = loc_df[loc_df['value']==1]
#     loc_df = cbyz.df_add_size(df=loc_df, group_by=['index'], col_name='count')
#     loc_df = loc_df[loc_df['count']==1]
#     loc_df = loc_df[['index', col]]
    
#     cond = []
#     for i in range(len(type_li)):
#         cond.append(loc_df[col]==type_li[i])
        
#     loc_df[col] = np.select(cond, value)
#     result = loc_df_raw.merge(loc_df, how='left', on='index')
#     return result
