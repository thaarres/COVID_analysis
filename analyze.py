import sys
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator
import glob
import numpy as np
from scipy.stats import norm
import datetime
import math

colorwheel = ['#FC766AFF','#783937FF','#F1AC88FF','#8c510a','#dfc27d','#01665e','#35978f','#bf812d','#f6e8c3','#c7eae5','#80cdc1']
linestyles = ['solid','dashed','dashdot','dashed']*3
colorwheelR = ['#fdd49e','#fdbb84','#fc8d59','#ef6548','#d7301f','#b30000','#7f0000']
colorwheelG = ['#ccece6','#99d8c9','#66c2a4','#41ae76','#238b45','#006d2c','#00441b']

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
    
  # Concatenate all case types into one data frame
  df_complete = pd.concat(df.values())
  df_complete['Date'] = pd.to_datetime(df_complete['Date'])

  df_ch = df_complete[df_complete['Country']==country]
  df_ch_Recovered = df_ch[df_ch['Type']=='Recovered']
  df_ch_Confirmed = df_ch[df_ch['Type']=='Confirmed']
  df_ch_Deaths = df_ch[df_ch['Type']=='Deaths']
  
  make_plots([df_ch_Confirmed,df_ch_Recovered,df_ch_Deaths],['Confirmed','Recovered','Deaths'],country,'JHU_cumulative_ts')
  
def getDailyJHU(country='Switzerland'):
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
  
  scale = [1.,1.,10.,10.]
  l0, = plt.plot(df['date'], scale[0]*df['ncumul_conf'].diff()    , color = colorwheelR[0], label = 'Confirmed x{}, Kanton {}'       .format(scale[0],kanton), linestyle=linestyles[0])
  l1, = plt.plot(df['date'], scale[1]*df['current_hosp']          , color = colorwheelG[1], label = 'Hospitalisations x{}, Kanton {}'.format(scale[1],kanton), linestyle=linestyles[1])
  l2, = plt.plot(df['date'], scale[2]*df['current_vent']          , color = colorwheelR[2], label = 'On ventilator x{}, Kanton {}'   .format(scale[2],kanton), linestyle=linestyles[2])
  l3, = plt.plot(df['date'], scale[3]*df['ncumul_deceased'].diff(), color = colorwheelG[3], label = 'Deaths x{}, Kanton {}'          .format(scale[3],kanton), linestyle=linestyles[3])
  plt.legend( loc='upper left')
  axes = plt.gca()
  # axes.set_ylim([0.0,0.5E4])
  axes.set_ylim(bottom=1)
  # axes.set_xlim([datetime.date(2020, 3, 1), datetime.date(2020, 10, 30)])
  # plt.yscale('log')
  plt.xlabel('Date')
  plt.ylabel('Daily cases')
  cfr = float(df["ncumul_deceased"].iloc[-1]/df["ncumul_conf"].iloc[-1])*100.
  if math.isnan(cfr):
    cfr = float(df["ncumul_deceased"].iloc[-2]/df["ncumul_conf"].iloc[-2])*100.
  plt.figtext(0.150, 0.53,'Case fatality rate {} = {:.2f}%'.format(kanton,cfr), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.83,'COVID-19 {}'.format(kanton), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.78,r'Open Data Kt. ZH / T. Aarrestad', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=5,maxticks=6))
  # plt.rc('grid', linestyle="-", color='black')
  # plt.grid(True)
  plt.savefig('covid_daily_CDH_{}.pdf'.format(kanton))
  plt.savefig('covid_daily_CDH_{}.png'.format(kanton))
  plt.close()
  
  # link2='https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_kanton_alter_geschlecht_csv/COVID19_Fallzahlen_Kanton_ZH_alter_geschlecht.csv' DEPRECATED AND REPLACED BY AGE GROUPS
  link2='https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_kanton_alter_geschlecht_csv/COVID19_Fallzahlen_Kanton_ZH_altersklassen_geschlecht.csv'
  #TODO! Add age group analysis per kanton    
      
def getDailyCH(kanton='all'):

  link = 'https://www.bag.admin.ch/dam/bag/en/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-bevoelkerungszahlen.xlsx.download.xlsx/Population_Size_BFS.xlsx'
  link = 'https://www.bag.admin.ch/dam/bag/en/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-fallzahlen.xlsx.download.xlsx/Dashboards_1&2_COVID19_swiss_data_pv.xlsx'
  link = 'https://www.bag.admin.ch/dam/bag/en/dokumente/mt/k-und-i/aktuelle-ausbrueche-pandemien/2019-nCoV/covid-19-basisdaten-labortests.xlsx.download.xlsx/Dashboard_3_COVID19_labtests_positivity.xlsx'
  
  df  = pd.read_excel(link)#
  print(df.info())
  df['fall_dt'][df.pttod_1 > 0] = df['pttoddat']
  df['fall_dt'] = pd.to_datetime(df['fall_dt'])
  df = df.sort_values(by='fall_dt')
  df_dead = df[df['pttod_1']> 0]
  df_dead = df_dead.groupby('akl', as_index=False).sum()  

  hist = df.plot(x='akl', y='pttod_1', style='o')
  hist.figure.savefig('death_per_age.png')

  scale = [1,1,1.,1]
  plot_lines = []
  fig, ax = plt.subplots()
  # plt.grid(color='0.8', linestyle='dotted')
  if kanton != 'all':
    
    df_kanton  = df[df['ktn']==kanton]
    print(df_kanton.head(10))
    l1, = plt.plot(df_kanton['fall_dt'], df_kanton['fallklasse_3']*scale[0], color = colorwheel[0], label = 'Confirmed x{} {}'.format(scale[0],kanton), linestyle=linestyles[0])
    l2, = plt.plot(df_kanton['fall_dt'], df_kanton['pttod_1']*scale[1]     , color = colorwheel[2], label = 'Deaths x{} {}'.format(scale[1],kanton), linestyle=linestyles[0])
  df_complete = df.groupby('fall_dt', as_index=False).sum()  
  l3, = plt.plot(df_complete['fall_dt'], df_complete['fallklasse_3']*scale[2], color = colorwheel[0], label = 'Confirmed x{}'.format(scale[2]), linestyle=linestyles[1])
  l4, = plt.plot(df_complete['fall_dt'], df_complete['pttod_1']*scale[3], color = colorwheel[2], label = 'Deaths x{}'.format(scale[3]), linestyle=linestyles[1])
  
  # plot_lines.append([l1,l2,l3])
  plt.legend( loc='upper left')
  axes = plt.gca()
  # axes.set_ylim([0.0,0.5E4])
  axes.set_ylim(bottom=1)
  # plt.yscale('log')
  plt.xlabel('Date')
  plt.ylabel('Daily cases')
  plt.figtext(0.620, 0.83,'COVID-19 {}'.format(kanton), wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.figtext(0.620, 0.78,r'BAG/ T. Aarrestad', wrap=True, horizontalalignment='left',verticalalignment='bottom')
  plt.gca().get_xaxis().set_major_locator(AutoDateLocator(minticks=4,maxticks=6))
  plt.savefig('covid_daily_BAG_{}.pdf'.format(kanton))
  plt.savefig('covid_daily_BAG_{}.png'.format(kanton))
  plt.close()

            
if __name__ == '__main__':     
  kanton = 'ZH'
  country = 'Switzerland'
  
  if len(sys.argv)>1:
    kanton = sys.argv[1]
  if len(sys.argv)>2:
    
    country = sys.argv[2]
      
  getDailyPerKanton(kanton)
  getDailyCH('all')
  
  
  getCumulativeJHU(country)
  getDailyJHU(country)
  




