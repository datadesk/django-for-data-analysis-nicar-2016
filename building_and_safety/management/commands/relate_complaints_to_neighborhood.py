import logging
from building_and_safety.models import Complaint, NeighborhoodV6
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help="Relate Complaints to Neighborhood objects"

    def handle(self, *args, **options):
        for neighborhood in NeighborhoodV6.objects.all():
            logger.debug("Setting complaint objects for %s" % neighborhood)
            neighborhood.set_complaint_objects()