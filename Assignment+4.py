
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[2]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[ ]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:


def get_list_of_university_towns():
    
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )  '''
    
     #The following cleaning needs to be done:
    '''1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    univ_towns = pd.read_csv('university_towns.txt', sep='\n', names=['RegionName'])
    filter1 = univ_towns['RegionName'].str.endswith('[edit]')
    univ_towns['States'] = univ_towns.where(filter1)
    univ_towns['States'].fillna(method = 'ffill', inplace = True)
    m
    univ_towns['RegionName'] = univ_towns['RegionName'].str.split('(', expand=True)[0]
    univ_towns['States'] = univ_towns['States'].str.split('[', expand=True)[0]
    univ_towns['RegionName'] = univ_towns['RegionName'].str.split('[', expand=True)[0]
    univ_towns['RegionName'] = univ_towns['RegionName'].str.strip()
    univ_towns['States'] = univ_towns['States'].str.strip()

    univ_towns = univ_towns[['States', 'RegionName']]
    univ_towns = univ_towns[univ_towns['States'] != univ_towns['RegionName']]

    return  univ_towns

get_list_of_university_towns()


# In[18]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    gdp_lev = pd.ExcelFile('gdplev.xls').parse(skiprows = 4)
    gdp_lev = gdp_lev[['Unnamed: 4','Unnamed: 6']]
    gdp_lev.columns = ['Year+Quarter', '2009 Chained GDP']
    gdp_lev.drop([0,1,2], inplace = True)
    #gdp_lev['Year+Quarter'] = str(gdp_lev['Year+Quarter']) why did this create new series for each index

    gdp_lev = gdp_lev.set_index('Year+Quarter')
    gdp_lev = gdp_lev['2000q1':]
    gdp_lev.reset_index(inplace=True)
    
    gdp_lev['Diff'] = gdp_lev['2009 Chained GDP'].diff()
    for ind,row in gdp_lev.iterrows():
        if gdp_lev.loc[ind, 'Diff'] < 0:
            if gdp_lev.loc[ind+1, 'Diff'] < 0:
                rec_start = gdp_lev.loc[ind, 'Year+Quarter']
                break
    
    return  rec_start

get_recession_start()


# In[19]:


def get_recession_end():
    gdp_lev = pd.ExcelFile('gdplev.xls').parse(skiprows = 4)
    gdp_lev = gdp_lev[['Unnamed: 4','Unnamed: 6']]
    gdp_lev.columns = ['Year+Quarter', '2009 Chained GDP']
    gdp_lev.drop([0,1,2], inplace = True)

    gdp_lev = gdp_lev.set_index('Year+Quarter')
    rec_start = get_recession_start()
    gdp_lev = gdp_lev[rec_start:]
    gdp_lev.reset_index(inplace=True)
    
    gdp_lev['Diff'] = gdp_lev['2009 Chained GDP'].diff()
    for ind,row in gdp_lev.iterrows():
        if gdp_lev.loc[ind, 'Diff'] > 0:
            if gdp_lev.loc[ind+1, 'Diff'] > 0:
                rec_end = gdp_lev.loc[ind+1, 'Year+Quarter']
                break
                
    return rec_end

get_recession_end()


# In[20]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    gdp_lev = pd.ExcelFile('gdplev.xls').parse(skiprows = 4)
    gdp_lev = gdp_lev[['Unnamed: 4','Unnamed: 6']]
    gdp_lev.columns = ['Year+Quarter', '2009 Chained GDP']
    gdp_lev.drop([0,1,2], inplace = True)

    gdp_lev = gdp_lev.set_index('Year+Quarter')
    rec_start = get_recession_start()
    rec_end = get_recession_end()
    gdp_lev = gdp_lev[rec_start: rec_end]
    gdp_lev.reset_index(inplace=True)
    gdp_lev['Diff'] = gdp_lev['2009 Chained GDP'].diff()

    rec_bottom = gdp_lev['2009 Chained GDP'].min()
    gdp_lev = gdp_lev[gdp_lev['2009 Chained GDP'] == rec_bottom]
    gdp_lev.set_index('Year+Quarter', inplace = True)
    
    return gdp_lev.index[0]

get_recession_bottom()


# In[21]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    import datetime as dt
    
    states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 
              'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 
              'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 
              'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 
              'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 
              'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 
              'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 
              'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 
              'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 
              'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 
              'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 
              'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 
              'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico',
              'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 
              'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 
              'ND': 'North Dakota', 'VA': 'Virginia'}
   
    housing_data = pd.read_csv('City_Zhvi_AllHomes.csv')
    '''A quarter is a specific three month period, Q1 is January through March,
    Q2 is April through June, Q3 is July through September, 
    Q4 is October through December.'''
    
    for col in housing_data.columns:
        if col.startswith('19'):
            housing_data.drop([col], axis = 1, inplace = True)
    
    housing_data.drop(['RegionID','Metro','CountyName','SizeRank'], axis = 1, inplace = True)
    housing_data = housing_data.set_index('State')

    for ind,row in housing_data.iterrows():
        housing_data.loc[ind, 'States'] = states[ind]
    
    housing_data = housing_data.set_index(['States','RegionName']).sort_index()
    housing_data.columns = pd.to_datetime(housing_data.columns)
    housing_data = housing_data.resample('Q', axis=1).mean()

    housing_data.rename(columns= lambda column: '{}q{}'.format(column.year, column.quarter), inplace = True)
        
    return housing_data

convert_housing_data_to_quarters()


# In[66]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. 
    
    University towns have their mean housing prices less effected by recessions.
    Run a t-test to compare the ratio of the mean price of houses in university 
    towns the quarter before the recession starts compared to the recession 
    bottom. (price_ratio=quarter_before_recession/recession_bottom)
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    rec_start = get_recession_start()
    rec_bottom = get_recession_bottom()
    housing_change = convert_housing_data_to_quarters()
    rec_pre = housing_change.columns[housing_change.columns.get_loc(rec_start)-1]
    housing_change = housing_change[[rec_pre,rec_bottom]]
    housing_change['Ratio'] = housing_change[rec_pre]/housing_change[rec_bottom]
    housing_change = housing_change.drop([rec_pre,rec_bottom],axis = 1)
    
    housing_change.reset_index(inplace = True)
    
    univ_towns = get_list_of_university_towns()
    univ_towns['Uni'] = True
    df= pd.merge(housing_change, univ_towns, how = 'left', on= ['States','RegionName'])
    df['Uni'] = df['Uni'].fillna(False)
    
    uni = df[df['Uni'] == True]
    non_uni = df[df['Uni'] == False]
    
    t,p = ttest_ind(uni['Ratio'].dropna(), non_uni['Ratio'].dropna())
    
    if p < 0.01:
        different = True
    else:
        different = False
        
    if uni['Ratio'].mean() < non_uni['Ratio'].mean():
        better = 'university town'
    else:
        better = 'non-university town'
    
    return different,p,better

run_ttest()


# In[ ]:




