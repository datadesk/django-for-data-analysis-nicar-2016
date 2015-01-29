Tk...

Goals
------
TKTKTK

Installation
------------
- pip install numpy==1.8.1 before requirements.txt (due to some bugs with numpy install)
- pip install -r requirements.txt

Database setup
--------------
- createdb django_data_analysis
- python manage.py syncdb
- python manage.py schemamigration building-and-safety --init
- python manage.py migrate 