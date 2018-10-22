import pandas as pd
import numpy as np

from lifelines import KaplanMeierFitter

from lifelines.statistics import logrank_test
from lifelines.statistics import multivariate_logrank_test
from lifelines.statistics import pairwise_logrank_test

import matplotlib.pyplot as plt

import re

#IMPORT DATA FROM CSV FILE
all_charts = pd.read_csv('Billboard Hot 100 from May 1961 to October 2018.csv',  encoding = "ISO-8859-1")

#PROCESSING THE CHARTS DATA 
#re-index the week column so that it's easier to see. Week 1 is the first week I have data for.
all_charts['Week'] = all_charts['Week'] + 3000

#for each entry, create a column for the date and date attribute
all_charts['Date'] = all_charts.Date.astype('datetime64')
all_charts['Year'] = pd.DatetimeIndex(all_charts['Date']).year
all_charts['Month'] = pd.DatetimeIndex(all_charts['Date']).month
all_charts['Day'] = pd.DatetimeIndex(all_charts['Date']).day
all_charts['Decade'] = all_charts['Year'] // 10

#TO MAKE TESTING FASTER
#all_charts = all_charts[all_charts['Year'] > 2010]

#fix a quirk that in the first week of the charts it's listed as 0
all_charts['Week on the Chart'] = all_charts.apply(lambda row: 1 if row['Total Weeks'] == 0 else row['Total Weeks'], axis = 1)
del all_charts['Total Weeks']

#label when songs left the charts, when they left for first time, and which entries are for after the first time leaving
#list the week that is the re-entry week, and it gives and NaN for weeks where it wasn't a re-entry
all_charts['Week of Reentry'] = all_charts.apply(lambda row: row['Week on the Chart'] if row['Week on the Chart'] > 1 and row['Last Position'] == 0 else 0, axis = 1)
#create a new dataframe that only has the re-entry weeks
reentry_songs = all_charts[['Title', 'Artist', 'Week of Reentry']]
reentry_songs = reentry_songs[reentry_songs['Week of Reentry'] > 0]
#for songs that have multitple re-entries, find the first one
reentry_songs = reentry_songs.groupby(['Title', 'Artist'], as_index = False).agg({'Week of Reentry': ['min']})
reentry_songs.columns = ['Title', 'Artist', 'Earliest Reentry Week']
reentry_songs['Reentry'] = 1
#in the all_charts dataframe, for songs that have a re-entry, list the first week of reentry
all_charts = pd.merge(all_charts, reentry_songs, how = 'left', on = ['Title', 'Artist'])
all_charts['Post First Reentry'] = all_charts.apply(lambda row: 1 if row['Reentry'] == 1 and row['Week on the Chart'] >= row['Week of Reentry'] else 0, axis = 1)
#delete all entries that are after the first re-entry
all_charts = all_charts[all_charts['Post First Reentry'] == 0]


#CREATE BASIC SONG-LEVEL DATA
by_song = all_charts.groupby(['Title', 'Artist'], as_index = False).agg({'Week on the Chart': ['max'], 'New': ['max'], 'Week': ['max', 'min'], 'Year': ['min'], 'Decade': ['min']})
by_song.columns = ['Title', 'Artist', 'Total Weeks in First Appearance', 'Not Left-Censored', 'Last Week', 'Entry Week', 'Entry Year', 'Entry Decade']
by_song['Total Weeks from Entry to Exit'] = by_song['Last Week'] - by_song['Entry Week'] + 1
by_song['Left-Censored'] = ~by_song['Not Left-Censored']
del by_song['Not Left-Censored']
#need to update this whenever I use a different number of weeks of data
by_song['Right-Censored'] = by_song.apply(lambda row: True if row['Entry Week'] == 3000 else False, axis = 1)
#this is done to test that all re-entries are being deleted
by_song['Missing Weeks'] = by_song['Total Weeks from Entry to Exit'] - by_song['Total Weeks in First Appearance']
#del by_song['Most Recent Week']
by_song['Event Observed'] = by_song.apply(lambda row: 0 if row['Right-Censored'] == True else 1, axis = 1)
by_song['Right-Censored'] = by_song.apply(lambda row: 1 if row['Right-Censored'] == True else 0, axis = 1)
by_song['Left-Censored'] = by_song.apply(lambda row: 1 if row['Left-Censored'] == True else 0, axis = 1)

#remove songs that are left-censored (might learn how to deal with them in the future)
by_song = by_song[by_song['Left-Censored'] ==  0]

#ADDING MORE FEATURES TO THE SONG LEVEL DATA
by_song['Featuring'] = by_song.apply(lambda row: 1 if 'Featuring' in row['Artist'] else 0, axis = 1)


#ANALYSIS

#BASIC KAPLAN-MEIER SURVIVAL MODEL - for all the data
kmf = KaplanMeierFitter()
kmf.fit(by_song['Total Weeks from Entry to Exit'], event_observed=by_song['Event Observed'], label = "all songs from 1961 to 2018")

plt.figure(1)
kmf.plot(ci_show = False)
plt.ylim(0, 1)
plt.xlim(0, 50)
plt.xticks(np.arange(0,50, step = 5))
plt.title("Time spent on Billboard Hot 100 Chart before first exit")
plt.savefig('Billboard Hot 100 - Kaplan-Meier Plot - 1961 to 2018.png')
plt.show()


#KAPLAN-MEIER SURVIVAL MODEL FOR THE LAST 4 YEARS


recent_years = by_song[by_song['Entry Year'] > 2013]
recent_years = recent_years[recent_years['Entry Year'] < 2018]

plt.figure(2)
ax = plt.subplot(1,1,1)
year_mask_2017 = (recent_years['Entry Year'] == 2017)
kmf_2017 = KaplanMeierFitter()
kmf_2017.fit(recent_years['Total Weeks in First Appearance'][year_mask_2017], event_observed = recent_years['Event Observed'][year_mask_2017], label = str(2017))
kmf_2017.plot(ax = ax, ci_show = False)    
year_mask_2016 = (recent_years['Entry Year'] == 2016)
kmf_2016 = KaplanMeierFitter()
kmf_2016.fit(recent_years['Total Weeks in First Appearance'][year_mask_2016], event_observed = recent_years['Event Observed'][year_mask_2016], label = str(2016))
kmf_2016.plot(ax = ax, ci_show = False) 
year_mask_2015 = (recent_years['Entry Year'] == 2015)
kmf_2015 = KaplanMeierFitter()
kmf_2015.fit(recent_years['Total Weeks in First Appearance'][year_mask_2015], event_observed = recent_years['Event Observed'][year_mask_2015], label = str(2015))
kmf_2015.plot(ax = ax, ci_show = False)    
year_mask_2014 = (recent_years['Entry Year'] == 2014)
kmf_2014 = KaplanMeierFitter()
kmf_2014.fit(recent_years['Total Weeks in First Appearance'][year_mask_2014], event_observed = recent_years['Event Observed'][year_mask_2014], label = str(2014))
kmf_2014.plot(ax = ax, ci_show = False)   

plt.ylim(0, 1)
plt.xlim(0, 30)
plt.xticks(np.arange(0, 30, step = 5))
plt.title("Time spent on Billboard Hot 100 Chart before first exit")
plt.savefig('Billboard Hot 100 - Kaplan-Meier Plot by Year 2014 to 2017.png')
plt.show()   
   
#test if the years 2017 and 2016 are different to a statistically significant level
results_2017_2016 = logrank_test(recent_years['Total Weeks in First Appearance'][year_mask_2017], recent_years['Total Weeks in First Appearance'][year_mask_2016], event_observed_A=recent_years['Event Observed'][year_mask_2017], event_observed_B=recent_years['Event Observed'][year_mask_2016])
#results_2017_2016.print_summary()
#They give a p-value of .2495 so are not statistically significant

#test if the years 2016 and 2015 are different to a statistically significant level
results_2016_2015 = logrank_test(recent_years['Total Weeks in First Appearance'][year_mask_2016], recent_years['Total Weeks in First Appearance'][year_mask_2015], event_observed_A=recent_years['Event Observed'][year_mask_2016], event_observed_B=recent_years['Event Observed'][year_mask_2015])
#results_2016_2015.print_summary()
#They give a p-value of .5160 so are not statistically significant

results_pw = pairwise_logrank_test(recent_years['Total Weeks in First Appearance'], recent_years['Entry Year'], recent_years['Event Observed'])

print(results_pw.iloc[0,1])
print(results_pw.iloc[0,2])
print(results_pw.iloc[0,3])
print(results_pw.iloc[1,2])
print(results_pw.iloc[1,3])
print(results_pw.iloc[2,3])


#EXAMINE DATA BY DECADE
plt.figure(3)
ax = plt.subplot(111)

year_mask_201 = (by_song['Entry Decade'] == 201)
kmf_201 = KaplanMeierFitter()
kmf_201.fit(by_song['Total Weeks in First Appearance'][year_mask_201], event_observed = by_song['Event Observed'][year_mask_201], label = '2010s')
kmf_201.plot(ax = ax, ci_show = False)    

year_mask_200 = (by_song['Entry Decade'] == 200)
kmf_200 = KaplanMeierFitter()
kmf_200.fit(by_song['Total Weeks in First Appearance'][year_mask_200], event_observed = by_song['Event Observed'][year_mask_200], label = '2000s')
kmf_200.plot(ax = ax, ci_show = False)   
 
year_mask_199 = (by_song['Entry Decade'] == 199)
kmf_199 = KaplanMeierFitter()
kmf_199.fit(by_song['Total Weeks in First Appearance'][year_mask_199], event_observed = by_song['Event Observed'][year_mask_199], label = '1990s')
kmf_199.plot(ax = ax, ci_show = False)    

year_mask_198 = (by_song['Entry Decade'] == 198)
kmf_198 = KaplanMeierFitter()
kmf_198.fit(by_song['Total Weeks in First Appearance'][year_mask_198], event_observed = by_song['Event Observed'][year_mask_198], label = '1980s')
kmf_198.plot(ax = ax, ci_show = False)  

year_mask_197 = (by_song['Entry Decade'] == 197)
kmf_197 = KaplanMeierFitter()
kmf_197.fit(by_song['Total Weeks in First Appearance'][year_mask_197], event_observed = by_song['Event Observed'][year_mask_197], label = '1970s')
kmf_197.plot(ax = ax, ci_show = False)  

year_mask_196 = (by_song['Entry Decade'] == 196)
kmf_196 = KaplanMeierFitter()
kmf_196.fit(by_song['Total Weeks in First Appearance'][year_mask_196], event_observed = by_song['Event Observed'][year_mask_196], label = '1960s')
kmf_196.plot(ax = ax, ci_show = False)  

plt.ylim(0, 1)
plt.xlim(0, 30)
plt.xticks(np.arange(0,50, step = 5))
plt.title("Time spent on Billboard Hot 100 Chart before first exit - by Decade")
plt.savefig('Billboard Hot 100 - Kaplan-Meier Plot by Decade - 1961 to 2018.png')

plt.show()


results_pw = pairwise_logrank_test(by_song['Total Weeks in First Appearance'], by_song['Entry Decade'], by_song['Event Observed'])

print(results_pw.iloc[0,1])
print(results_pw.iloc[0,2])
print(results_pw.iloc[0,3])
print(results_pw.iloc[0,3])
print(results_pw.iloc[0,4])
print(results_pw.iloc[0,5])
print(results_pw.iloc[1,2])
print(results_pw.iloc[1,3])
print(results_pw.iloc[1,4])
print(results_pw.iloc[1,5])
print(results_pw.iloc[2,3])
print(results_pw.iloc[2,4])
print(results_pw.iloc[2,5])
print(results_pw.iloc[3,4])
print(results_pw.iloc[3,5])
print(results_pw.iloc[4,5])