# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 10:45:17 2023

@author: CarlWhelan
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

def convert_dates(date_string):
    
    yr=str(datetime.now().year)
    date_string_split=date_string.split()
    wkday=date_string_split[0]
    day=date_string_split[1][:-2]
    mth=date_string_split[2]
    
    tm=date_string_split[3]
    date_string_cleaned=" ".join([wkday,day,mth,yr,tm])
    dtformat="%A %d %B %Y %H:%M"

    dt=datetime.strptime(date_string_cleaned,dtformat)
    return dt

def semiparsed_to_df(semiparsed):
    keys=['Date','HomeTeam','HomeGoals','AwayGoals','KOTime','AwayTeam','Status']
    list_results=[]
    date_tag='h4'
    for item in semiparsed:
        if str(item)[:len(date_tag)+1]=='<'+date_tag:
            date=item.get_text()
        else:
            result_txt=item.get_text()
            result_entry=[res for res in result_txt.replace('\n','').split('  ') if len(res)>0]
            result={}
            result['Date']=date
            for i in range(1,len(keys)):
                result[keys[i]]=result_entry[i-1]
            list_results.append(result)
    df=pd.DataFrame(list_results)
    #Convert text Date and Time to single Datetime
    df['Datetime']=(df.Date + ' ' + df.KOTime).apply(convert_dates)
    df.drop(columns=['Date','KOTime'],inplace=True)    
    
    cols_reordered=['Datetime','HomeTeam','HomeGoals','AwayTeam','AwayGoals','Status']
    df=df[cols_reordered]
    return df
    
def scrape_pl_results():
    url='https://www.skysports.com/premier-league-results'
    soup=BeautifulSoup(requests.get(url).text)
    tags=['h4','div'] #h4 tags contain the dates, div tags contain result information
    classes=['fixres__header2','fixres__item'] #corresponding classes
    s_parsed=soup.find_all(tags,class_=classes)
    return(semiparsed_to_df(s_parsed))



