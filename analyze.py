#!/usr/bin/env python

"""analyze.py: 
Analyze COVID data from three different sources:
JHU, BAG and Open Data ZH. Plots per kanton/country.
"""

__author__      = "Thea Aarrestad"
__version__     = "1.0.0"
__maintainer__  = "Thea Aarrestad"
__email__       = "thea.aarrestad@cern.ch"

import sys
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator
import glob
import numpy as np
from scipy.stats import norm
import datetime
import math

from scipy.optimize import curve_fit
from scipy.stats import expon
import matplotlib.mlab as mlab

def func(x, a,c):
    return a+np.exp(c*x)
    

colorwheel  = ['#7a5195','#ef5675','#ffa600','#003f5c']
linestyles  = ['solid','dashed','dotted','dashdot']*3


def make_plots(datas,legends,country,oname):
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
    axes.set_xlim([datetime.date(2020, 3, 1), datetime.date.today()])
    plt.yscale('log')
    plt.xlabel('Date')
    plt.ylabel('Cumulative count')
    plt.figtext(0.625, 0.18,'COVID-19 {}'.format(country), wrap=True, horizontalalignment='left',verticalalignment='bottom')
    plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=4,maxticks=6))
    plt.savefig('{}_{}.pdf'.format(oname,country))
    plt.savefig('{}_{}.png'.format(oname,country))
    plt.close()

def getCumulativeJHU(country='Switzerland'):
  data = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{}_global.csv'
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
    
  df_complete = pd.concat(df.values())
  df_complete['Date'] = pd.to_datetime(df_complete['Date'])

  df_ch = df_complete[df_complete['Country']==country]
  df_ch_Recovered = df_ch[df_ch['Type']=='Recovered']
  df_ch_Confirmed = df_ch[df_ch['Type']=='Confirmed']
  df_ch_Deaths = df_ch[df_ch['Type']=='Deaths']
  
  make_plots([df_ch_Confirmed,df_ch_Recovered,df_ch_Deaths],['Confirmed','Recovered','Deaths'],country,'JHU_cumulative_ts')
  
def getDailyJHU(country='Switzerland'):
  #  #   Column     Non-Null Count  Dtype
  # ---  ------     --------------  -----
  #  0   Date       259 non-null    datetime64[ns]
  #  1   Confirmed  259 non-null    float64
  #  2   Recovered  259 non-null    float64
  #  3   Deaths     259 non-null    float64
  categories = ['Confirmed', 'Recovered', 'Deaths']
  datapath ='COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'
  
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
  df_complete.fillna(0)
  print(df_complete.info())
  print(df_complete.tail(30))
  #622 2020-10-22 04:24:27    91763.0    54600.0  2039.0-->106 deaths 
  scale = [1.,1.,10.]

  fig, ax = plt.subplots()
  y1, x1, patches1 = plt.hist(x=df_complete['Date'], weights=df_complete['Confirmed'].diff()*scale[0]  , bins=len(df_complete['Date']), facecolor = colorwheel[0], edgecolor =  'black', label = 'Confirmed'   , linestyle=linestyles[0], linewidth=0.15)
  # y2, x2, patches2 = plt.hist(x=df_complete['Date'], weights=df_complete['Recovered'].diff()*scale[1]  , bins=len(df_complete['Date']), facecolor = colorwheel[1], edgecolor =  'black', label = 'Recovered'   , linestyle=linestyles[0], linewidth=0.15)
  y3, x3, patches3 = plt.hist(x=df_complete['Date'], weights=df_complete['Deaths']   .diff()*scale[2]  , bins=len(df_complete['Date']), facecolor = colorwheel[2], edgecolor =  'black', label = 'Deaths x{} '.format(scale[2]), linestyle=linestyles[0], linewidth=0.15)
  y3 = (y3[np.logical_not(np.isnan(y3))])
  idx = np.where(y3 == y3.max())
  print(float(x3[idx]))
  
  axes = plt.gca()
  # axes.set_ylim([0.0,0.5E4])
  axes.set_ylim(bottom=0.0)
  axes.set_xlim([datetime.date(2020, 4, 1), datetime.date.today()])
  # plt.yscale('log')
  plt.axhline(y=y3.max(), color=colorwheel[2], linestyle='dashed',label='Max deaths = {}'.format(int(y3.max()/scale[2])))
  plt.legend( loc='upper left')
  plt.xlabel('Date')
  plt.ylabel('Daily cases')
  print(df_complete.tail(10))
  cfr = float(df_complete["Deaths"].iloc[-1]/df_complete["Confirmed"].iloc[-1])*100.
  plt.figtext(0.150, 0.53,'Case fatality rate {} = {:.2f}%'.format(country,cfr), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  # plt.figtext(0.150, 0.43,'Max. deaths/day = {}'.format(int(y3.max())/scale[2]), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  
  plt.figtext(0.620, 0.83,'COVID-19 {}'.format(country), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.78,r'JHU CSSE', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=4,maxticks=6))
  plt.grid(color='black', linestyle='dotted', linewidth=0.3)
  plt.savefig('JHU_daily_ts_{}.pdf'.format(country))
  plt.savefig('JHU_daily_ts_{}.png'.format(country))
  plt.close()
  
def getDailyPerKanton(kanton):
  # #   Column
  # --  ------
  # 0   date
  # 1   time
  # 2   abbreviation_canton_and_fl
  # 3   ncumul_tested
  # 4   ncumul_conf
  # 5   new_hosp
  # 6   current_hosp
  # 7   current_icu
  # 8   current_vent
  # 9   ncumul_released
  # 10  ncumul_deceased
  # 11  source
  # 12  current_isolated
  # 13  current_quarantined
  # 14  current_quarantined_riskareatravel
  # 15  current_quarantined_total
  link ='http://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total_v2.csv'
  df  = pd.read_csv(link)#
  print(df.info())
  df['date'] = pd.to_datetime(df['date'])
  df = df.sort_values(by='date')
  df  = df[df['abbreviation_canton_and_fl']==kanton]
  df = df.groupby('date', as_index=False).sum()
  
  scale = [1.,1.,1.,10.]
  l0,x0,p0 = plt.hist(x=df['date'], weights=scale[0]*df['ncumul_conf'].diff()    , bins=len(df['date'])+1, facecolor = colorwheel[0], edgecolor =  'black', label = 'Confirmed x{}, Kanton {}'       .format(scale[0],kanton), linestyle=linestyles[0], linewidth=0.15,alpha=0.8)
  l1,x1,p1 = plt.hist(x=df['date'], weights=scale[1]*df['current_hosp']          , bins=len(df['date'])+1, facecolor = colorwheel[1], edgecolor =  'black', label = 'Hospitalisations x{}, Kanton {}'.format(scale[1],kanton), linestyle=linestyles[0], linewidth=0.15,alpha=0.8)
  l2,x2,p2 = plt.hist(x=df['date'], weights=scale[2]*df['current_vent']          , bins=len(df['date'])+1, facecolor = colorwheel[2], edgecolor =  'black', label = 'On ventilator x{}, Kanton {}'   .format(scale[2],kanton), linestyle=linestyles[0], linewidth=0.15,alpha=0.8)
  l3,x3,p3 = plt.hist(x=df['date'], weights=scale[3]*df['ncumul_deceased'].diff(), bins=len(df['date'])+1, facecolor = colorwheel[3], edgecolor =  'black', label = 'Deaths x{}, Kanton {}'          .format(scale[3],kanton), linestyle=linestyles[0], linewidth=0.15,alpha=0.8)
  plt.legend( loc='upper left')
  axes = plt.gca()
  # axes.set_ylim([0.0,0.5E4])
  axes.set_ylim(bottom=1)
  axes.set_xlim([datetime.date(2020, 4, 1), datetime.date.today()])
  # plt.yscale('log')
  plt.xlabel('Date')
  plt.ylabel('Daily cases')
  cfr = float(df["ncumul_deceased"].iloc[-1]/df["ncumul_conf"].iloc[-1])*100.
  if math.isnan(cfr):
    cfr = float(df["ncumul_deceased"].iloc[-2]/df["ncumul_conf"].iloc[-2])*100.
  plt.figtext(0.150, 0.53,'Case fatality rate {} = {:.2f}%'.format(kanton,cfr), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.83,'COVID-19 {}'.format(kanton), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.78,r'Open Data Kt. ZH', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=5,maxticks=6))
  # plt.rc('grid', linestyle="-", color='black')
  # plt.grid(True)
  plt.savefig('OpenDataZH_covid_daily_{}.pdf'.format(kanton))
  plt.savefig('OpenDataZH_covid_daily_{}.png'.format(kanton))
  plt.close()
  
  # link2='https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_kanton_alter_geschlecht_csv/COVID19_Fallzahlen_Kanton_ZH_alter_geschlecht.csv' DEPRECATED AND REPLACED BY AGE GROUPS
  link2='https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_kanton_alter_geschlecht_csv/COVID19_Fallzahlen_Kanton_ZH_altersklassen_geschlecht.csv'
  #TODO! Add age group analysis per kanton    
      
def getDailyCH(kanton='all'):
  #link_labtests = 'https://www.bag.admin.ch/dam/bag/en/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-labortests.xlsx.download.xlsx/Dashboard_3_COVID19_labtests_positivity.xlsx'
  link_demographics = 'https://www.bag.admin.ch/dam/bag/en/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-bevoelkerungszahlen.xlsx.download.xlsx/Population_Size_BFS.xlsx'
  link = 'https://www.bag.admin.ch/dam/bag/en/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx'
  # 0   replikation_dt  811533 non-null  datetime64[ns]
  # 1   fall_dt         404548 non-null  object
  # 2   ktn             811533 non-null  object
  # 3   akl             811533 non-null  object
  # 4   sex             811533 non-null  int64
  # 5   Geschlecht      811533 non-null  object
  # 6   Sexe            811533 non-null  object
  # 7   fallklasse_3    811533 non-null  int64
  # 8   pttoddat        203294 non-null  object
  # 9   pttod_1         811533 non-null  int64
  df  = pd.read_excel(link)#
  df_demographics  = pd.read_excel(link_demographics)
  df_demographics = df_demographics.groupby('akl', as_index=False).sum()  
  
  df['fall_dt'][df.pttod_1 > 0] = df['pttoddat']
  df['fall_dt'] = pd.to_datetime(df['fall_dt'])
  df = df.sort_values(by='fall_dt')
  df_dead = df#[df['pttod_1']> 0]
  df_dead["akl"] = df_dead["akl"].astype("|S")
  df_dead = df_dead[df_dead["akl"] != b'Unbekannt']
  df_dead = df_dead.groupby('akl', as_index=False).sum()  

  array = [0,15,25,35,45,55,65,75,80]
  
  df_dead['ind'] = pd.Series(array)
  df_demographics['ind'] = pd.Series(array)
  print(df_dead.info())
  print(df_dead.head(100))
  fig, ax = plt.subplots()
  # plt.figure(figsize=(3,5))
  
  l1, = plt.plot(df_dead['ind'], 100*0.1*df_dead['fallklasse_3']/df_demographics['pop_size'], color = colorwheel[3],label='0.1 * Confirmed/total population per age group', linestyle=linestyles[0], marker='8')
  l2, = plt.plot(df_dead['ind'], 100*df_dead['pttod_1']/df_demographics['pop_size'], color = colorwheel[0],label='Deaths/total population per age group', linestyle=linestyles[0], marker='8')

  plt.legend( loc='upper right',frameon=False)
  plt.xlabel('Age')
  plt.ylabel('Cases (% total population per age group)')
  axes = plt.gca()
  axes.set_ylim([0.0,0.6])
  # plt.yscale('log')
  # axes.set_ylim(bottom=0.0,top=2200.)
  plt.figtext(0.130, 0.83,'COVID-19 Switzerland', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.130, 0.78,r'BAG', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.savefig('BAG_deaths_confirmed_per_ageclass.png')
  
  fig, ax = plt.subplots()
  axes = plt.gca()
  axes.set_ylim([0.0,2200.])
  # l1, = plt.plot(df_dead['ind'], df_dead['fallklasse_3'], color = colorwheel[3],label='Confirmed cases', linestyle=linestyles[0], marker='8')
  l3, = plt.plot(df_dead['ind'], df_dead['pttod_1'], color = colorwheel[0],label='Deaths', linestyle=linestyles[0], marker='8')
  popt, pcov = curve_fit(func,  df_dead['ind'], df_dead['pttod_1'])
  plt.plot(  df_dead['ind'], func(df_dead['ind'], *popt), 'g--', label='fit: y=%5.3f+exp(%5.3f*x)' % tuple(popt))
  plt.legend( loc='upper right',frameon=False)
  plt.xlabel('Age')
  plt.ylabel('Total deaths')
  axes = plt.gca()
  # axes.set_ylim([0.0,0.5E4])
  # plt.yscale('log')
  # axes.set_ylim(bottom=0.0,top=2000.)
  plt.figtext(0.130, 0.83,'COVID-19 Switzerland', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.130, 0.78,r'BAG', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.savefig('BAG_fit_deaths_per_ageclass.png')
  
  scale = [1,100.,1.,100.]
  plot_lines = []
  fig, ax = plt.subplots()
  # plt.grid(color='0.8', linestyle='dotted')
  if kanton != 'all':
    
    df_kanton  = df[df['ktn']==kanton]
    l1, = plt.plot(df_kanton['fall_dt'], df_kanton['fallklasse_3']*scale[0], color = colorwheel[0], label = 'Confirmed x{} {}'.format(scale[0],kanton), linestyle=linestyles[0])
    l2, = plt.plot(df_kanton['fall_dt'], df_kanton['pttod_1']*scale[1]     , color = colorwheel[2], label = 'Deaths x{} {}'.format(scale[1],kanton), linestyle=linestyles[0])
  df_complete = df.groupby('fall_dt', as_index=False).sum()  
  y1, x1, patches1 = plt.hist(x=df_complete['fall_dt'], weights=df_complete['fallklasse_3']*scale[2]  , bins=len(df_complete['fall_dt']), facecolor = colorwheel[0], edgecolor =  'black', label = 'Confirmed x{}'.format(scale[2]), linestyle=linestyles[0], linewidth=0.15)
  y2, x2, patches2 = plt.hist(x=df_complete['fall_dt'], weights=df_complete['pttod_1']     *scale[3]  , bins=len(df_complete['fall_dt']), facecolor = colorwheel[1], edgecolor =  'black', label = 'Deaths x{}'.format(scale[3])   , linestyle=linestyles[0], linewidth=0.15)

  plt.legend( loc='upper left')
  axes = plt.gca()
  # axes.set_ylim([0.0,0.5E4])
  axes.set_ylim(bottom=1)
  axes.set_xlim([datetime.date(2020, 4, 1),datetime.date(2020, 11, 9)])# datetime.date.today()])
  # plt.yscale('log')
  plt.xlabel('Date')
  plt.ylabel('Daily cases')
  plt.figtext(0.620, 0.83,'COVID-19 {}'.format(kanton), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.78,r'BAG', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=4,maxticks=6))
  plt.savefig('BAG_covid_daily_{}.pdf'.format(kanton))
  plt.savefig('BAG_covid_daily_{}.png'.format(kanton))
  plt.close()

            
if __name__ == '__main__':  
  country = 'Switzerland'
  if len(sys.argv)>1:
    kanton = sys.argv[1]
  if len(sys.argv)>2:
    country = sys.argv[2]
      
  getDailyPerKanton(kanton)
  getDailyCH('all')
  getDailyJHU(country)
  getCumulativeJHU(country)


#Not yet used: # https://www.covid19.admin.ch/api/data/20201111-rrxnz6kp/downloads/sources-csv.zip



