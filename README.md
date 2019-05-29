# scraper-US-top-cities-data
scraper-US-top-cities-data is a scraper to collect data from Wikipedia (as well as city-data.com) about the top cities in the United States using Python.

## Summary
This project aims to collect top cities of US primarily from Wikipedia as well city-data.com. The city numbers is determined by users. The fields collected from those data sources
after cleanning are: (Total 21 fields)

|            Field name |     Field name      |      Field name   |     Field name         |
| :---------------------| :-------------------| :-----------------| :----------------------|       
|  Population 2018 rank |        Name         |    State          |Population 2018 estimate|
| Population 2010 census| Change(%,2010-2018) |Land area 2016(sqmi)|Land area 2016(km2)    |
|Population density 2016(sqmi) |Population density 2016(km2)|  Location(N,W)|Elevation     |
|         Mayor         |       Time zone     |     Website       |         Area code      |
|         Demonym       |Male-female percentage|Median household income|Mean_housing_price |
|Living index           |                      |                  |                        |

['Population 2018 rank','Name','State','Population 2018 estimate','Population 2010 census',
'Change(%,2010-2018)','Land area 2016(sqmi)','Land area 2016(km2)','Population density 2016(sqmi)',
'Population density 2016(km2)','Location(N,W)','Elevation','Mayor','Time zone','Website','Area code','Demonym',
'Male-female percentage','Median household income','Mean_housing_price','Living index']

The city number has upper limit of 314 based on the original wikipedia page
However, as city numbers go over 100, the usage of google-search api is not stable (will be blocked), the add of time delay before using google search api helps prevent the problem.

The city data is saved as csv format file (actually US_cities.txt, with comma seperated),
This file has been tested to be uploaded to goolge BigQuery.

## Set up to run

### Prerequisites
The code are implemented in Python 3.6.4, to install Python, see: [Python 3.6 ](https://www.python.org/downloads/release/python-360/). 

The main packages or libarary are: Beautifulsoup4, google 

```bash
pip install bs4

pip install google
```
There is a simple GUI program which requires Tk.(Also tk in built in libaray in python, there is a chance you still need install it anyway)
```bash
pip install python-tk
```
### Run the main GUI

Run the main_GUI_CITY_INFO.py will start collecting data.

After running the main function, input the city number(default is 100) and press the "Search" button, wait for the program to run for a while, the final data will be automatically saved in a file named "US_cities.txt" with "," as seperator.

## Samples procedure 
### Data collecting procedure
See attached pictures : city_parsing.JPG, gui.JPG, gui2.JPG
