from django.contrib.gis.db import models
from django.db.models import Q
from datetime import datetime

class OlderThanOneYearManager(models.GeoManager):
    """
    Get all complaints that are older than one year from July 13, 2014, 
    since complaints that aren't a year old yet are of no use to us.
    """
    def get_query_set(self):
        return super(OlderThanOneYearManager, self).get_query_set().filter(
            date_received__lte=datetime(2013, 7, 13)
        )
