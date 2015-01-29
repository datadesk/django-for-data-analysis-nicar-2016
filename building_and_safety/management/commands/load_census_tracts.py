import os
import logging
from django.conf import settings
from building_and_safety.models import CensusTract
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand, CommandError
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Loads L.A. City census tracts into the database'
    data_dir = os.path.join(settings.ROOT_DIR,
                            'building_and_safety/data/census_tracts')

    def handle(self, *args, **options):
        logger.debug("Loading census tract data")
        shp = os.path.join(self.data_dir, '2010Tracts.shp')
        db2shp = {
            'polygon_4326': 'POLYGON',
            'tract_id': 'GEOID10',
        }
        lm = LayerMapping(CensusTract, shp, db2shp, encoding='latin-1')
        lm.save()
