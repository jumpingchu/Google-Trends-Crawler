#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import json
import re
from datetime import datetime, timedelta
from tqdm import tqdm
import os
import typing

# ---
### Functions

# 處理 "相關查詢" 欄位
def relatedQueries_proc(target):
    if target == []:
        target = '---'
    else:
        result = ''
        for relatedQuery in target:
            target = result + relatedQuery['query'] + ' / '
    
    return target

def trends_crawler(str_date: str, country: str) -> pd.DataFrame:
    url = f'https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&geo={country}&ns=15&ed={str_date}'
    resp = requests.get(url)

    # 文字處理
    df = pd.DataFrame(json.loads(re.sub(r'\)\]\}\',\n', '', resp.text))['default']['trendingSearchesDays'][0]['trendingSearches'])

    # 欄位處理
    df = df.drop(columns='shareUrl')
    df['title'] = df['title'].apply(lambda x: x['query'])
    df['articles'] = df['articles'].apply(lambda x: x[0]['title'])
    df['relatedQueries'] = df['relatedQueries'].apply(relatedQueries_proc)
    try:
        df['image'] = df['image'].apply(lambda x: x['newsUrl'])
    except:
        pass
    df.columns = ['關鍵字', '搜尋筆數', '相關查詢', '文章連結', '相關文章']

    # 欄位移動
    col = '文章連結'
    move = df.pop(col)
    df.insert(4, col, move)
    
    return df

# ---

end_date = datetime.today()
start_date = end_date - timedelta(days=29)
str_end_date = datetime.strftime(end_date, '%Y%m%d')
str_start_date = datetime.strftime(start_date, '%Y%m%d')

# ### TW
for i in tqdm((pd.date_range(start=start_date, end=end_date, freq='1D'))):
    str_i_date = datetime.strftime(i, '%Y%m%d')
    ndf = trends_crawler(str_i_date, 'TW')
    ndf['date'] = str_i_date
    with open(f'./data_tw/{str_i_date}.pkl', 'wb') as f:
        ndf.to_pickle(f)


# ### JP
for i in tqdm((pd.date_range(start=start_date, end=end_date, freq='1D'))):
    str_i_date = datetime.strftime(i, '%Y%m%d')
    ndf = trends_crawler(str_i_date, 'JP')
    ndf['date'] = str_i_date
    with open(f'./data_jp/{str_i_date}.pkl', 'wb') as f:
        ndf.to_pickle(f)


#---
### 讀取檔案

### TW
df_tw = []
for file in os.listdir('data_tw'):
    if 'pkl' in file:
        df_file = pd.read_pickle('./data_tw/' + file)
        df_tw.append(df_file)


# ### 更新 TW 字典
with open('./keyword_tw.txt', 'r', encoding='utf8') as f:
    kw_list = [kw.strip() for kw in f.readlines()]
    
new_kw = []
for data in df_tw:
    new_kw += [kw + '\n' for kw in data['關鍵字'] if kw.strip() not in kw_list]
print(new_kw)

with open('./keyword_tw.txt', 'a+', encoding='utf8') as f:
    f.writelines(''.join(list(set(new_kw))))


# ### JP
df_jp = []
for file in os.listdir('data_jp'):
    if 'pkl' in file:
        df_file = pd.read_pickle('./data_jp/' + file)
        df_jp.append(df_file)


### 更新 JP 字典
with open('./keyword_jp.txt', 'r', encoding='utf-8') as f:
    kw_list = [kw.strip() for kw in f.readlines()]

new_kw = []
for data in df_jp:
    new_kw += [kw + '\n' for kw in data['關鍵字'] if kw.strip() not in kw_list]
print(new_kw)

with open('./keyword_jp.txt', 'a+', encoding='utf8') as f:
    f.writelines(''.join(list(set(new_kw))))

