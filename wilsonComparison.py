# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 14:28:32 2021

@author: Windows
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

tickers = ['BEKE','GRVY']

#list of tickers whose financial data needs to be extracted
financial_dir_cy = {} #directory to store current year's information
financial_dir_py = {} #directory to store last year's information
financial_dir_py2 = {} #directory to store last to last year's information

for ticker in tickers:
    try:
        print("scraping financial statement data for ",ticker)
        temp_dir = {}
        temp_dir2 = {}
        temp_dir3 = {}
    #getting balance sheet data from yahoo finance for the given ticker
        url = 'https://in.finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
        page = requests.get(url)
        page_content = page.content
        soup = BeautifulSoup(page_content,'html.parser')
        tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
        for t in tabl:
            rows = t.find_all("div", {"class" : "rw-expnded"})
            for row in rows:
                temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1]
                temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]
        
        #getting income statement data from yahoo finance for the given ticker
        url = 'https://in.finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
        page = requests.get(url)
        page_content = page.content
        soup = BeautifulSoup(page_content,'html.parser')
        tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
        for t in tabl:
            rows = t.find_all("div", {"class" : "rw-expnded"})
            for row in rows:
                temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1]
                temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]
        
        #getting cashflow statement data from yahoo finance for the given ticker
        url = 'https://in.finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
        page = requests.get(url)
        page_content = page.content
        soup = BeautifulSoup(page_content,'html.parser')
        tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
        for t in tabl:
            rows = t.find_all("div", {"class" : "rw-expnded"})
            for row in rows:
                temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1]
                temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3] 
        
        #combining all extracted information with the corresponding ticker
        financial_dir_cy[ticker] = temp_dir
        financial_dir_py[ticker] = temp_dir2
        financial_dir_py2[ticker] = temp_dir3
    except:
        print("Problem scraping data for ",ticker)


#storing information in pandas dataframe
combined_financials_cy = pd.DataFrame(financial_dir_cy)
#combined_financials_cy.dropna(axis=1,inplace=True) #dropping columns with NaN values
combined_financials_py = pd.DataFrame(financial_dir_py)
#combined_financials_py.dropna(axis=1,inplace=True)
combined_financials_py2 = pd.DataFrame(financial_dir_py2)
#combined_financials_py2.dropna(axis=1,inplace=True)
tickers = combined_financials_cy.columns #updating the tickers list based on only those tickers whose values were successfully extracted

# selecting relevant financial information for each stock using fundamental data
stats = ["Total revenue","Cost of revenue","Net income available to common shareholders","Free cash flow","Goodwill",
         "Net cash provided by operating activities"] # change as required

indx = ["revenue","cost","NetIncome","fcashflow","Goodwill","CashFlowOps"]


def info_filter(df,stats,indx):
    """function to filter relevant financial information for each 
       stock and transforming string inputs to numeric"""
    tickers = df.columns
    all_stats = {}
    for ticker in tickers:
        try:
            temp = df[ticker]
            ticker_stats = []
            for stat in stats:
                ticker_stats.append(temp.loc[stat])
            all_stats['{}'.format(ticker)] = ticker_stats
        except:
            print("can't read data for ",ticker)
    
    all_stats_df = pd.DataFrame(all_stats,index=indx)
  
    
    # cleansing of fundamental data imported in dataframe
    all_stats_df[tickers] = all_stats_df[tickers].replace({',': ''}, regex=True)
    for ticker in all_stats_df.columns:
        all_stats_df[ticker] = pd.to_numeric(all_stats_df[ticker].values,errors='coerce')
    return all_stats_df
def calculator(number1,number2,number3):
    if number2 == 0:
        return number1-number2
    elif number1 == number2 and number2 != 0:
        return (number1-number3)/abs(number3)
    else:
        return (number1-number2)/abs(number2)

def wilson_score(df_cy,df_py,df_py2):
    """function to calculate f score of each stock and output information as dataframe"""
    f_score = {}
    tickers = df_cy.columns
    for ticker in tickers:
        revenue_FS= calculator(df_cy.loc["revenue",ticker],df_py.loc["revenue",ticker],df_py2.loc["revenue",ticker])
        cost_FS=calculator(df_cy.loc["cost",ticker],df_py.loc["cost",ticker],df_py2.loc["cost",ticker])
        income_FS = calculator(df_cy.loc["NetIncome",ticker],df_py.loc["NetIncome",ticker],df_py2.loc["NetIncome",ticker])
        cash_FS = calculator(df_cy.loc["fcashflow",ticker],df_py.loc["fcashflow",ticker],df_py2.loc["fcashflow",ticker])
        Goodwill_FS=calculator(df_cy.loc["Goodwill",ticker],df_py.loc["Goodwill",ticker],df_py2.loc["Goodwill",ticker])
        CFO_FS = df_cy.loc["CashFlowOps",ticker]
        f_score[ticker] = [revenue_FS,cost_FS,income_FS,cash_FS,Goodwill_FS,CFO_FS]
    f_score_df = pd.DataFrame(f_score,index=["revenueDiff","costDiff","incomeDiff","freecashflowDiff","GoodWillDiff","PosCashFlowOperation"])
    return f_score_df


# Selecting stocks with highest Piotroski f score
transformed_df_cy = info_filter(combined_financials_cy,stats,indx)
transformed_df_py = info_filter(combined_financials_py,stats,indx)
transformed_df_py2 = info_filter(combined_financials_py2,stats,indx)

w_score_df = wilson_score(transformed_df_cy,transformed_df_py,transformed_df_py2)
w_score_df.to_csv(r'c:\Users\windows\w_score_df.csv')
wSum=w_score_df.sum().sort_values(ascending=False)
print(wSum)