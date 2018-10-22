# Billboard-Charts---Survival-Analysis

I have started looking into data from the Billboard music charts. 
I was able to easily get the data using Allan Guo's billboards package: https://github.com/guoguo12/billboard-charts .

How long do songs stay in the Hot 100 chart once they enter?

This was the first quesion I wanted to answer, so I processed the data a bit to be able to use the lifelines package. I plotted a few Kaplan-Meier estimators for all my data and a few subsets (individual years and individual decades).

As I started doing this with data from the last few years, I noticed something peculiar in the plots. There was a huge dropoff at 20 weeks. Up until 20 weeks the dropoff was relatively consistent, but all of the sudden it went from a maximum of 5 percent of existing songs leaving to about 1/3 of them leaving, and then proceeding again to a relatively consistent rate. I assumed something was wrong with my code, but a quick look at the dataframes in Anaconda didn't lead me anywhere. Then I decided to do some outside research and found out something quite interesting - Billboard manually removes "recurrent" songs according to some specific criteria. Currently, for the Hot 100 chart, they remove songs that have been in the chart for 20 weeks and are outside the top 50, or have been on the chart for 52 weeks and are outside of the top 25 (the rules have changed over the years, and there are some exceptions for re-releases or other special cases). So that oddity in the data was explained.

Looking at some of the recent full years of data (2014 - 2017) showed some variation, but using the log-rank test showed it to not be statistically signficant. 

However, when I looked at the survival curve by decade, there were some real trends to see and statistically significant details. In the 2010s, there are a lot more songs that only enter the chart for one week and then leave. I will have to do some more research into figuring out what happens with these songs. Do they only drop out for one week and then return? Or are they really one and done? This will be relatively easy to find out with the data I downloaded - it will just take a bit of time. 

Ignoring the 2010s, there was a trend of songs staying on the charts longer and longer. In the 1990s about 1/3 of songs stayed on the charts for at least 20 weeks. This is what lead to Billboard deciding to start removing recurrent songs (the practice began in 1991, though ). 

It's also important to say that what the charts actually track has changed over the years. In the 1960s there was of course no Spotify streaming or social media sharing. Both of those now count towards the ranking. So any look at how long songs stay on the charts has as much to do with the way Billboard ranks them as the way people listen to music.

