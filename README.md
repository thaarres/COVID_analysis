**COVID analyzer for Switzerland (Based on JHU and Gesundheitsdirektion ZH data)**


The JHU data is a submodule of this repository, so before analyzing makes sure you fetch the latest data
```python
cd COVID-19
git pull
cd ..
```

Crawling data from
https://github.com/CSSEGISandData/COVID-19
and
https://github.com/openZH/covid_19/

To run 
```python
python3 analyze.py kanton country #kanton for BAG data, country for JHU data
```


