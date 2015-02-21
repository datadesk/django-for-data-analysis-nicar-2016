# Django for Data Analysis #

## Who are we, and what are we doing here? ##
So you know some SQL, or maybe done data analysis with R, but would prefer a more integrated way to explore and publish data. 

In addition to making front-facing web apps, Django can also be used internally as a reporting and research tool to explore a dataset. 

To do this, we'll use a publicly available dataset from the [City of L.A.'s data portal](https://data.lacity.org/) on [response times to complaints](https://data.lacity.org/browse?q=building%20and%20safety%20customer%20service%20request&sortBy=relevance&utf8=%E2%9C%93) filed to the Department of Building and Safety. We used this data to publish a [story on the varying response times](http://www.latimes.com/local/cityhall/la-me-building-safety-delay-20141219-story.html) to DBS complaints throughout the city, including especially slow response times on the Eastside.  

We'll learn how to:
- Load data from a CSV into Django models,  
- Create queries and views to help us analyze the data,
- Use these views to create tables and vizualizations that we can use for publication.  

## Setup ##

### Installation ###
```bash
$ pip install numpy==1.8.1 before requirements.txt ( we have to install numpy first due to some bugs with the numpy install )
$ pip install -r requirements.txt
```

### Database setup ###
```bash
$ createdb django_data_analysis
$ python manage.py syncdb
$ python manage.py schemamigration building_and_safety --init
$ python manage.py migrate 
```

## Getting started: The Models ##
- First, let's look at our models. There are a couple of fields we're concerned with or need more explanation.
  - **csr** - this is a complaint ID, and can serve as our primary key
  - **ladbs_inspection_district** - How LADBS divides their inspectors, one per district. After reporting this out further we found that these actually change quite a bit from year-to-year.
  - **date_received** - date the complaint was received.
  - **date_closed** - "Closed" is a funny term here. This is actually the date that an inspector visited the location of a complaint. In many cases this is when an inspector determines whether a complaint is valid or not. So really "closed" just means an inspector has visited a complaint.
  - **date_due** - arbitrary measure of time that the LADBS would like to address a complaint by. They apparently don't place a whole lot of meaning on this, and not all complaints have due dates.
  - **csr_priority** - This is the priority level that LADBS responds to the complaints. Level 1 is often life-threatening, level 2 is quality of life issues, and level 3 is more like a nuisance.
  - **area_planning_commission** - one of the seven different planning department areas the complaint is located in. We used this and the neighborhood level for most of our analysis. 
  - **response_days** - good reason to vet your data. We realized this was calculated differently for open and closed days, so was essentially useless. Instead we calculated this on our own. 


- There are also a few fields that we're calculating on load 
  - **full_address** - caching the address by concatenating the seven different types of address field in the data
  - **is_closed** - easier way to find whether a case is "closed" or not. 
  - **days_since_complaint** - basically a useful version of the **response_days** field above. Calculated by finding the difference between the date received and the date closed. 
  - **gt_30_days**, **gt_90_days**, **gt_180_days**, **more_than_one_year** - different booleans to make it easy to access cases of a certain age level. 


- load Complaints data

```bash
$ python manage.py load_complaints
```

This command creates a Complaint record for every row in our two csvs. Note that instead of saving every individual record as it's loaded, we use Django's bulk_create method to create them in batches of 500. This saves a ton of time as we're not hitting the database for row in the CSV.

## What are we looking at here? Exploring the data ##
We can use basic Django commands to get a feel the data we're looking at. 

```bash
$ python manage.py shell
```

Let's use this to answer a couple of basic questions about the data:
- How many complaints do we have total?
- How many are still unaddressed?
- How many complaints went more than a year before being addressed?

```bash
>>> from building_and_safety.models import *
>>> complaints = Complaint.objects.all()
>>> complaints.count()
71120
>>> complaints.filter(is_closed=False).count()
4060
>>> complaints.filter(more_than_one_year=True).count()
1231
```

Whats happening behind the scenes? Django's converting all of our queries to SQL, and executing them on the database. 

We can see these, and it's helpful to see exactly what Django's trying to do when you're having trouble with a query.

```bash
>>> from django.db import connection
>>> print connection.queries[-1]
{u'time': u'0.028', u'sql': u'SELECT COUNT(*) FROM "building_and_safety_complaint" WHERE "building_and_safety_complaint"."more_than_one_year" = true '}
```

We can use this for more complicated questions too. 
- How are the complaints older than one year distributed throughout the planning commissions? Are some worse than others?

```bash
>>> from django.db.models import Count
>>> complaints.filter(more_than_one_year=True).values('area_planning_commission').annotate(count=Count("csr")).order_by('-count')
[{'count': 618, 'area_planning_commission': u'East Los Angeles'}, {'count': 394, 'area_planning_commission': u'Central'}, {'count': 86, 'area_planning_commission': u'West Los Angeles'}, {'count': 60, 'area_planning_commission': u'South Valley'}, {'count': 56, 'area_planning_commission': u'South Los Angeles'}, {'count': 8, 'area_planning_commission': u'North Valley'}, {'count': 7, 'area_planning_commission': u''}, {'count': 2, 'area_planning_commission': u'Harbor'}]
```

Now we're on to something.

## Views: Documenting and replicating your work ##
One advantage of using Django is that all of our data manipulation can be stored in the views, and the output displayed in HTML templates. 

We've already created a few views that start to explore the data, so let's start exploring. 

Exit the python interpreter, if you still have it running, by pressing `CTRL-D`, and start the Django server.

```bash
$ fab rs
Removing .pyc files
[localhost] local: python manage.py runserver 0.0.0.0:8000
Validating models...

0 errors found
February 20, 2015 - 16:40:36
Django version 1.6.5, using settings 'project.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

Open up the views.py file in your text editor, and look at the `class ComplaintAnalysis(TemplateView)`

