## COVID-19 analyzer (Based on JHU and Gesundheitsdirektion ZH data)

Crawling and plotting data from
https://github.com/CSSEGISandData/COVID-19
and
https://github.com/openZH/covid_19/

#### Prerequisites
This code runs in Python 3.7, with the following dependencies:
```console
scipy==1.4.1
numpy==1.18.0
matplotlib==3.1.2
pandas==1.1.3
```

 To install the pre-requisites, do
```console
pip3 install -r requirements.txt
```

The JHU data is a submodule of this repository, so before analyzing makes sure you fetch the latest data
```console
cd COVID-19/
git pull
cd ../
```

#### To run

The script takes two arguments:The first is `kanton` and it defines what is plotted using BAG data, the second is `country` and it defines which contry data is plotted using JHU data 
```console
python3 analyze.py kanton country #kanton for BAG data, country for JHU data
```


