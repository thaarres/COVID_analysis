import sys
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator
import glob
import numpy as np
from scipy.stats import norm

colorwheel = ['#FC766AFF','#783937FF','#F1AC88FF','#8c510a','#dfc27d','#01665e','#35978f','#bf812d','#f6e8c3','#c7eae5','#80cdc1']
linestyles = ['dotted','solid','solid','dashdot','dashed']

def gaussian(x, amp, cen, wid):
    return amp * np.exp(-(x-cen)**2 / wid)
    
def make_plots(datas,legends,country):
    scale = [1.,1.,10.]
    linestyles = ['dotted','dashed','solid','dashdot']
    plot_lines = []
    fig, ax = plt.subplots()
    # plt.grid(color='0.8', linestyle='dotted')
    for i,(data,legend) in enumerate(zip(datas,legends)):
      print(legend)
      print(data)                                         
      l1, = plt.plot(data['Date'], data['Count'] , color = colorwheel[i], linestyle=linestyles[i])
      plot_lines.append([l1])
    plt.legend([l[0] for l in plot_lines], legends, loc='upper left')
    axes = plt.gca()
    axes.set_ylim([1E2,5E5])
    plt.yscale('log')
    plt.xlabel('Date')
    plt.ylabel('Cumulative count')
    plt.figtext(0.625, 0.18,'COVID-19 Switzerland', wrap=True, horizontalalignment='left',verticalalignment='bottom')
    plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=4,maxticks=6))
    plt.savefig('covid_ts_{}.pdf'.format(country))
    plt.savefig('covid_ts_{}.png'.format(country))
    plt.close()

def getCumulative(country='Switzerland'):
  data = 'csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{}_global.csv'
  categories = ['Confirmed', 'Deaths', 'Recovered']
  df = dict()
  for cat in categories:     
      df[cat] = pd.read_csv(data.format(cat))   

  for field, dfi in df.items(): 
      dfi = dfi.groupby('Country/Region', as_index=False).sum()
      dfi = dfi.melt(id_vars=['Country/Region', 'Lat', 'Long'], value_name='Count')
      dfi['Type'] = field
      dfi.columns =  ['Country', 'Latitude', 'Longitude', 'Date', 'Count', 'Type']    # Replace the dataframe in the global dataframe dictionary
      df[field] = dfi
    
  # Concatenate all case types into one data frame
  df_complete = pd.concat(df.values())
  df_complete['Date'] = pd.to_datetime(df_complete['Date'])

  df_ch = df_complete[df_complete['Country']==country]
  df_ch_Recovered = df_ch[df_ch['Type']=='Recovered']
  df_ch_Confirmed = df_ch[df_ch['Type']=='Confirmed']
  df_ch_Deaths = df_ch[df_ch['Type']=='Deaths']
  
  make_plots([df_ch_Confirmed,df_ch_Recovered,df_ch_Deaths],['Confirmed','Recovered','Deaths'],country)
  
def getDaily(country='Switzerland'):
  categories = ['Confirmed', 'Recovered', 'Deaths']
  datapath = 'csse_covid_19_data/csse_covid_19_daily_reports/'
  
  df = dict()
  
  for filename in glob.glob('{}/*.csv'.format(datapath)):
    date = (filename[:-4].split('/')[-1])
    datai  = pd.read_csv(filename)#
    try:
      data = datai[datai['Country/Region']==country]
    except:
      data = datai[datai['Country_Region']==country]
    data['Date'] = pd.to_datetime(date)
    try:
      data['Date'] = pd.to_datetime(data['Last Update'])
    except:
      data['Date'] = pd.to_datetime(data['Last_Update'])
    df[date] = data[['Date','Confirmed', 'Recovered', 'Deaths']]
    
  df_complete = pd.concat(df.values())
  df_complete = df_complete.sort_values(by='Date')
  # print(df_complete.info())
  print(df_complete.head(100))
  scale = [1.,1.,100.]
  plot_lines = []
  fig, ax = plt.subplots()
  # plt.grid(color='0.8', linestyle='dotted')
  l1, = plt.plot(df_complete['Date'], df_complete['Confirmed'].diff()*scale[0]  , color = colorwheel[0], label = 'Confirmed', linestyle=linestyles[0])
  l2, = plt.plot(df_complete['Date'], df_complete['Recovered'].diff()*scale[1]  , color = colorwheel[1], label = 'Recovered', linestyle=linestyles[1])
  l3, = plt.plot(df_complete['Date'], df_complete['Deaths'].diff()*scale[2]    , color = colorwheel[2], label = 'Deaths x100 ', linestyle=linestyles[2])
  # plot_lines.append([l1,l2,l3])
  plt.legend( loc='upper left')
  axes = plt.gca()
  # axes.set_ylim([0.0,0.5E4])
  axes.set_ylim(bottom=0.0)
  # plt.yscale('log')
  plt.xlabel('Date')
  plt.ylabel('Daily cases')
  plt.figtext(0.620, 0.83,'COVID-19 {}'.format(country), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.78,r'JHU CSSE / T. Aarrestad', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=4,maxticks=6))
  plt.savefig('covid_daily_{}.pdf'.format(country))
  plt.savefig('covid_daily_{}.png'.format(country))
  plt.close()
            
if __name__ == '__main__':     
  
  country = 'Switzerland'
  getCumulative(country)
  getDaily(country)
  




