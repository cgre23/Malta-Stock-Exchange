import re
import os
import csv
from collections import defaultdict
import pandas as pd
from pathlib import Path # For data paths
import numpy as np
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import streamlit as st

st.set_page_config(
    layout="centered", page_icon="🖱️", page_title="Malta Bonds YTM Calculator"
)
st.title("🖱️ Malta Bonds Yield-to-Maturity Calculator")
st.write(
    """This app calculates the YTM for the Malta Corporate Bonds."""
)

def tableDataText(table):    
    """Parses a html segment started with tag <table> followed 
    by multiple <tr> (table rows) and inner <td> (table data) tags. 
    It returns a list of rows with inner columns. 
    Accepts only one <th> (table header/data) in the first row.
    """
    def rowgetDataText(tr, coltag='td'): # td (data) or th (header)       
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]  
    rows = []
    trs = table.find_all('tr')
    headerow = rowgetDataText(trs[0], 'th')
    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs: # for every table row
        rows.append(rowgetDataText(tr, 'td') ) # data row       
    return rows


headers = {'Accept-Encoding': 'identity'}
try:
    response = requests.get("https://www.borzamalta.com.mt/?handler=TradingBoard", headers=headers)
except requests.ConnectionError as error:
    print(error)
    
list_table=[]
bs = BeautifulSoup(response.content)
tables = bs.findAll('table')
for table in tables:
    df = pd.DataFrame(tableDataText(table))
    if len(df.index) > 15:
        df=df.rename(columns=df.iloc[0]).drop(df.index[0])
        list_table.append(df)
        
offers = list_table[-3].set_index('Symbol Code')
offers = offers.replace('-', np.NaN)
offers['Best Offer Price'] = offers['Best Offer Price'].astype(float)
offers['Best Bid Count'] = offers['Best Bid Count'].astype(float)
offers['Best Bid Price'] = offers['Best Bid Price'].astype(float)
offers['Yield'] = offers['Security Name'].str.extract('((?:\d+%)|(?:\d+\.\d+%))')
offers['Maturity'] = offers['Security Name'].str.extract('(2\d\d\d)').astype(int)
offers['YTM'] = (((offers['Yield'].str.rstrip('%').astype('float')) + (100-offers['Best Offer Price'])/(offers['Maturity']-2023))*100 / ((100+offers['Best Offer Price'])/2))
offers['YTM'] = np.round(offers['YTM'],2)
offers = offers.sort_values(by=['YTM'], ascending=False)

st.dataframe(offers)

