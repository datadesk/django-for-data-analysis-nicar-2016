<pre><code>     _  _                                    _        _     _                  _      _       
  __| |(_)__ _ _ _  __ _ ___   _ __ _ _ ___ (_)___ __| |_  | |_ ___ _ __  _ __| |__ _| |_ ___ 
 / _` || / _` | ' \/ _` / _ \ | '_ \ '_/ _ \| / -_) _|  _| |  _/ -_) '  \| '_ \ / _` |  _/ -_)
 \__,_|/ \__,_|_||_\__, \___/ | .__/_| \___// \___\__|\__|  \__\___|_|_|_| .__/_\__,_|\__\___|
     |__/          |___/      |_|         |__/                           |_|                  
</code></pre>

A custom template for initializing a new Django project the Data Desk way. 

Uses the [built-in](https://docs.djangoproject.com/en/1.5/ref/django-admin/#startproject-projectname-destination) Django ``startproject`` templating system. Includes a number of small modifications favored by the [Los Angeles Times Data Desk](http://datadesk.latimes.com). Assumes you already have experience hacking around on Django and PostGIS.

Still experimental, so don't get your hopes up.

[![Build Status](https://travis-ci.org/datadesk/django-project-template.png?branch=master)](https://travis-ci.org/datadesk/django-project-template)
[![Coverage Status](https://coveralls.io/repos/datadesk/django-project-template/badge.png?branch=master)](https://coveralls.io/r/datadesk/django-project-template?branch=master)

* Issues: [https://github.com/datadesk/django-project-template/issues](https://github.com/datadesk/django-project-template/issues)
* Testing: [https://travis-ci.org/datadesk/django-project-template](https://travis-ci.org/datadesk/django-project-template)
* Coverage: [https://coveralls.io/r/datadesk/django-project-template](https://coveralls.io/r/datadesk/django-project-template)

Features
--------

* A split of ``settings.py`` that allows for different values in [development](https://github.com/datadesk/django-project-template/blob/master/project_name/settings_dev.template) versus [production](https://github.com/datadesk/django-project-template/blob/master/project_name/settings_prod.py)
* Preinstallation of Django's [automatic administration panel](https://docs.djangoproject.com/en/dev/ref/contrib/admin/)
* Preconfiguration of [urls.py](https://github.com/datadesk/django-project-template/blob/master/project_name/urls.py) to serve static, media and Munin files
* Preconfiguration of [logging options](https://github.com/datadesk/django-project-template/blob/master/project_name/settings.py#L104)
* Preconfiguration of [GeoDjango](https://docs.djangoproject.com/en/dev/ref/contrib/gis/) for [PostGIS](http://postgis.net/)
* Preinstallation of [South](http://south.readthedocs.org/en/latest/) migrations
* Preinstallation of [django-debug-toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar)
* Preinstallation of [django-greeking](https://github.com/palewire/django-greeking)
* [Fabric functions](https://github.com/datadesk/django-project-template/blob/master/fabfile.py) for local development and production deployment
* Preinstallation of [tools for interacting with Amazon Web Services](https://code.google.com/p/boto/)
* Preconfiguration of our preferred caching options for [development](https://github.com/datadesk/django-project-template/blob/master/project_name/settings_dev.template#L14) and [production](https://github.com/datadesk/django-project-template/blob/master/project_name/settings_prod.py#L14)
* [Chef cookbook](https://github.com/datadesk/django-project-template/tree/master/chef) with scripted production server configuration routines
* Management commands for scheduling [database backups](https://github.com/datadesk/django-project-template/blob/master/toolbox/management/commands/backupdb.py) to be stored in a bucket on Amazon S3 and [retrieving them](https://github.com/datadesk/django-project-template/blob/master/toolbox/management/commands/loadbackupdb.py) for local installation.
* Custom context processors that provide the [current site](https://github.com/datadesk/django-project-template/blob/master/toolbox/context_processors/sites.py) and [environment](https://github.com/datadesk/django-project-template/blob/master/toolbox/context_processors/env.py).
* A number of goofball utilities, like a [unicode CSV reader](https://github.com/datadesk/django-project-template/blob/master/toolbox/unicodecsv.py)

Requirements
------------

* [Django 1.6](https://www.djangoproject.com/download/)
* [PostGIS](https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#installation)
* [virtualenv](http://www.virtualenv.org/en/latest/)

Getting started
---------------

Create a virtual enviroment to work inside.

```bash
$ virtualenv my-environment
```

Jump in and turn it on.

```bash
$ cd my-environment
$ . bin/activate
```

Install Django.

```bash
$ pip install django
```

Create a new Git repository.

```bash
$ git init repo
```

Download and install a project in there using this template.

```bash
$ django-admin.py startproject --extension=py,.gitignore --template=https://github.com/datadesk/django-project-template/archive/master.zip project repo
```

Now that the template has landed, jump in and install the project's Python dependencies.

```bash
$ cd repo
$ pip install -r requirements.txt
```

Generate a secret key.

```bash
$ fab generate_secret
```

Copy the key. Open the settings file and drop it near the top. While you're there, you can also customize any of the other top level configuration options.

```bash
$ vim project/settings.py
```

Create a PostGIS database to connect with. This may vary depending on your PostGIS configuration. 

The command below assumes you have it running and want to make the database with a user named ``postgres``. Please modify it to suit your needs. If you don't have PostGIS installed, try following [the GeoDjango installation instructions](https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#installation).

```bash
$ createdb -U postgres -E UTF8 -T template_postgis mydatabasename
```

Make a copy of the development settings template.

```bash
$ cp project/settings_dev.template project/settings_dev.py
```

Open it and put in the credentials for the database you just made.

```bash
$ vim project/settings_dev.py
```

Sync the database.

```bash
$ python manage.py syncdb
```

Fire up the test server.

```bash
$ fab rs
```

Get to work. Once you have something worth saving you can replace this README with a description of your new project. 
