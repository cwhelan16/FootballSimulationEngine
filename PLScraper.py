# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 10:45:17 2023

@author: CarlWhelan
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

import manipulate

def convert_dates(date_string):
    
    
    date_string_split=date_string.split()
    wkday=date_string_split[0]
    day=date_string_split[1][:-2]
    mth=date_string_split[2]
    if mth in ['August','September','October','November','December']:
        yr=str(2023)
    else:
        yr=str(2024) #THIS IS REALLY CRAP BUT I WANTED A QUICK FIX
    
    tm=date_string_split[3]
    date_string_cleaned=" ".join([wkday,day,mth,yr,tm])
    dtformat="%A %d %B %Y %H:%M"

    dt=datetime.strptime(date_string_cleaned,dtformat)
    return dt

def semiparsed_to_df(semiparsed,fixtype='result'):
    if fixtype not in ['result','fixture']:
        print('Error: Invalid fixture type.')
        return None
    elif fixtype == 'result':
        keys=['Date','HomeTeam','HomeGoals','AwayGoals','KOTime','AwayTeam','Status']
    else: #fixture
        keys=['Date','HomeTeam','HomeGoals','AwayGoals','KOTime','AwayTeam']
    list_results=[]
    date_tag='h4'
    num_cols=['HomeGoals','AwayGoals'] #numerical columns which are initially returned as strings
    for item in semiparsed:
        if str(item)[:len(date_tag)+1]=='<'+date_tag:
            date=item.get_text()
        else:
            result_txt=item.get_text()
            result_entry=[res.strip() for res in result_txt.replace('\n',' ').split('  ') if len(res)>0]
            result={}
            result['Date']=date
            for i in range(1,len(keys)):
                result[keys[i]]=result_entry[i-1]
            list_results.append(result)
    df=pd.DataFrame(list_results)
    #Convert text Date and Time to single Datetime
    df['Datetime']=(df.Date + ' ' + df.KOTime).apply(convert_dates)
    df.drop(columns=['Date','KOTime'],inplace=True)    
    
    if fixtype=='result':
        cols_reordered=['Datetime','HomeTeam','HomeGoals','AwayTeam','AwayGoals','Status']
    else:#fixture
        cols_reordered=['Datetime','HomeTeam','HomeGoals','AwayTeam','AwayGoals']
    df=df[cols_reordered]
    df=manipulate.df_strings_to_numbers(df,num_cols)
    return df
    
def scrape_pl_results():
    url='https://www.skysports.com/premier-league-results'
    soup=BeautifulSoup(requests.get(url).text,features='lxml')
    tags=['h4','div'] #h4 tags contain the dates, div tags contain result information
    classes=['fixres__header2','fixres__item'] #corresponding classes
    s_parsed=soup.find_all(tags,class_=classes)
    
    results_df=semiparsed_to_df(s_parsed)
    return results_df

def scrape_pl_fixtures():
    url='https://www.skysports.com/premier-league-fixtures'
    soup=BeautifulSoup(requests.get(url).text,features='lxml')
    tags=['h4','div'] #h4 tags contain the dates, div tags contain result information
    classes=['fixres__header2','fixres__item'] #corresponding classes
    s_parsed=soup.find_all(tags,class_=classes)
    return semiparsed_to_df(s_parsed,fixtype='fixture')