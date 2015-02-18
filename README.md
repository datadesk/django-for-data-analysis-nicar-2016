# Django for Data Analysis #

## Who are we, and what are we doing here? ##
So you know some SQL, or maybe done data analysis with R, but would prefer a more integrated way to explore and publish data. 

Using the Django framework, you can load, manipulate data, and create visualizations in HTML templates, all within the same app.

To do this, we'll use a publicly available dataset from the [City of L.A.'s data portal](https://data.lacity.org/) on [response times to complaints](https://data.lacity.org/browse?q=building%20and%20safety%20customer%20service%20request&sortBy=relevance&utf8=%E2%9C%93) filed to the Department of Building and Safety, as well as our [Mapping L.A. neighborhoods](http://boundaries.latimes.com/sets/). 

## Setup ##

### Installation ###
- pip install numpy==1.8.1 before requirements.txt ( we have to install numpy first due to some bugs with the numpy install )
- pip install -r requirements.txt

### Database setup ###
- createdb django_data_analysis
- python manage.py syncdb
- python manage.py schemamigration building_and_safety --init
- python manage.py migrate 

## Getting started: The Models ##
- load Complaints data
`python manage.py load_complaints`
This command creates a Complaint record for every row in our two csvs. 

### What are we looking at here? ###