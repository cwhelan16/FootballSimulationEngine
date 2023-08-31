# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 13:15:13 2023

@author: CarlWhelan
"""

import pandas as pd
from pandasql import sqldf

def rename_cols(df,prevcolnames,newcolnames):
    df.rename(columns=dict(zip(prevcolnames,newcolnames)),inplace=True)
    return df

def rename_vals(string,prevvals,newvals):
    for i in range(len(prevvals)):
        if string==prevvals[i]:
            string=newvals[i]
    return string

def df_rename_vals(df,cols,prevvals,newvals):
    for col in cols:
        df[col]=df[col].apply(lambda x: rename_vals(x,prevvals,newvals))
    return df

def update_df(curr_df_name,new_df_name):
    query='''
    WITH FINAL AS
    (
     SELECT Datetime, HomeTeam, HomeGoals, AwayTeam, AwayGoals, Status
    FROM %s
    
    UNION ALL
    
    SELECT Datetime, HomeTeam, HomeGoals, AwayTeam, AwayGoals, Status
    FROM %s
    WHERE
    Datetime > (SELECT MAX(Datetime) FROM %s)
    AND Status='FT'
    )
    SELECT *
    FROM FINAL
    ORDER BY Datetime DESC;
    '''%(curr_df_name,new_df_name,curr_df_name)
    
    newdf=sqldf(query,locals())
    return newdf

def df_strings_to_numbers(df,cols):
    for col in cols:
        df[col]=df[col].apply(lambda x: int(x))
    return df



