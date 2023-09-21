# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 10:31:49 2023

@author: CarlWhelan
"""

import numpy as np
import pandas as pd

def get_rates(hometeam,awayteam,dataset,num_games=10,method=1):
    '''
    Function to get transition rates for hometeam and awayteam scoring respectively.
    Inputs:
    hometeam - name of home team as in dataset
    awayteam - name of away team as in dataset
    dataset - dataset of historical results. This function expects the dataset input to have the following columns:
        Date - of the given historical fixture
        HomeTeam - name of the home team in a given fixture
        HomeGoals - number of goals scored by HomeTeam in a given fixture
        AwayTeam -name of the away team in a given fixture
        AwayGoals - number of goals scored in a given fixture
        Additionally, dataset must be sorted by descending Date (i.e. most recent historical fixtures occur first)
    num_games - number of historical figures to average over
    method - method for calculating the transition rates:
        1. Average of goals scored by team in the last num_games and goals conceded by their opponent in the last num_games
    '''
    num_games_home=min(len(dataset.Datetime[(dataset.HomeTeam==hometeam)|(dataset.AwayTeam==hometeam)]),num_games)
    dates_home=dataset.Datetime[(dataset.HomeTeam==hometeam)|(dataset.AwayTeam==hometeam)].reset_index(drop=True)
    earliest_date_home=dates_home[num_games_home-1]
    home_goals_for=np.sum(dataset.HomeGoals[dataset.HomeTeam==hometeam][dataset.Datetime>=earliest_date_home])+ np.sum(dataset.AwayGoals[dataset.AwayTeam==hometeam][dataset.Datetime>=earliest_date_home])
    home_goals_against=np.sum(dataset.AwayGoals[dataset.HomeTeam==hometeam][dataset.Datetime>=earliest_date_home])+ np.sum(dataset.HomeGoals[dataset.AwayTeam==hometeam][dataset.Datetime>=earliest_date_home])
    
    num_games_away=min(len(dataset.Datetime[(dataset.AwayTeam==awayteam)|(dataset.HomeTeam==awayteam)]),num_games)
    dates_away=dataset.Datetime[(dataset.AwayTeam==awayteam)|(dataset.HomeTeam==awayteam)].reset_index(drop=True)
    earliest_date_away=dates_away[num_games_away-1]
    away_goals_for=np.sum(dataset.AwayGoals[dataset.AwayTeam==awayteam][dataset.Datetime>=earliest_date_away])+ np.sum(dataset.HomeGoals[dataset.HomeTeam==awayteam][dataset.Datetime>=earliest_date_away])
    away_goals_against=np.sum(dataset.AwayGoals[dataset.HomeTeam==awayteam][dataset.Datetime>=earliest_date_away])+ np.sum(dataset.HomeGoals[dataset.AwayTeam==awayteam][dataset.Datetime>=earliest_date_away])
    
    if method==1:
        rate_home=(home_goals_for/num_games_home + away_goals_against/num_games_away)/2
        rate_away=(away_goals_for/num_games_away + home_goals_against/num_games_home)/2
    
    return [rate_home,rate_away]

def gillespie(rates,rseed=None):
    '''
    Gillespie algorithm to model the result of a football match as MJP with transition rate from score
    [n,m]->[n+1,m] as rate[0], the rate at which the home team scores
    and
    [n,m]->[n,m+1] as rate[1], the rate at which the away team scores.
    MJP is modelled over a time interval of 1 game.
    '''
    score=[0,0]
    if rseed is not None:
        np.random.set_state(rseed)
    t=0
    while t<1:
        dt=np.random.exponential(scale=1/sum(rates))
        whoscored=np.random.choice([0,1],p=rates/sum(rates))
        score[whoscored]+=1
        t+=dt
    return score


def predict_result(hometeam,awayteam,dataset,num_games=10,method=1,num_simulations=1000,return_all_sims=False):
    rates=get_rates(hometeam,awayteam,dataset,num_games=num_games,method=method)
    res=[]
    for i in range(num_simulations):
        res.append(gillespie(rates))
    res=np.array(res)
    n_home_wins=len(res[res[:,0]>res[:,1]])
    n_away_wins=len(res[res[:,0]<res[:,1]])
    n_draws=num_simulations-n_home_wins-n_away_wins
    p_home_win, p_away_win, p_draw = n_home_wins/num_simulations, n_away_wins/num_simulations, n_draws/num_simulations
    if return_all_sims:
        res_out=res
    else:
        res_out=None
    return {'ProbHomeWin':p_home_win,'ProbAwayWin':p_away_win,'ProbDraw':p_draw,'FullSimulatedResults':res_out}

def predict_multiple_results(fixture_df,results_df,history=10,method=1,num_simulations=1000):
    predictions=[]
    hometeams=fixture_df.HomeTeam
    awayteams=fixture_df.AwayTeam
    dates=fixture_df.Datetime
    for i in range(len(hometeams)):
        matchinfo={'Datetime':dates[i],'HomeTeam':hometeams[i],'AwayTeam':awayteams[i]}
        sim_res=predict_result(hometeams[i],awayteams[i],results_df,
                               num_games=history, method=method, 
                               num_simulations=num_simulations,
                               return_all_sims=False)
        entry={**matchinfo,**sim_res}
        predictions.append(entry)
    return pd.DataFrame(predictions)
