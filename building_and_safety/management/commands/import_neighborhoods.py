# -*- coding: utf-8 -*-
import os
import unicodecsv
from django.conf import settings
from building_and_safety.models import NeighborhoodV6
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Loads version six of Los Angeles Times meighborhood boundaries with associated demographics'
    data_dir = os.path.join(settings.ROOT_DIR, 'building_and_safety/data/neighborhoods_v6')
    model_list = [NeighborhoodV6]

    def handle(self, *args, **options):
        print "Loading NeighborhoodsV6 data"
        self.verbosity = int(options['verbosity'])
        self.flush_models()
        self.load_shapes()
        self.set_population()

    def flush_models(self):
        print "- Flushing data tables"
        for m in self.model_list:
            if self.verbosity > 1:
                print "-- %s" % m.__name__
            m.objects.all().delete()

    def set_population(self):
        """
        Merge census population data with the NeighborhoodV6 models in our database
        """
        print "- Loading populations"
        # Get the data
        path = os.path.join(self.data_dir, 'neighborhoods_stats_V6.tsv')
        reader = unicodecsv.DictReader(open(path, 'r'), delimiter="\t")
        data = [(i['Name'].strip(), i['TotPopUniv'], i['PopPerSqMile']) for i in reader]

        # Loop through and load it in
        for name, pop, persqmile in data:
            try:
                obj = NeighborhoodV6.objects.filter(has_statistics=True).get(name=name)
                obj.population = float(pop)
                obj.density = float(persqmile)
                obj.population_source = 'Census 2010'
            except NeighborhoodV6.DoesNotExist:
                continue
            obj.save()
            if self.verbosity > 1:
                print "-- %s" % obj.name

    def load_shapes(self):
        """
        Load the neighborhood shapes for Los Angeles and Orange County
        """
        print "- Loading shapes"
        # Load shape file
        shp = os.path.join(self.data_dir, 'neighborhoods_v6.shp')
        db2shp = {
            'polygon_4326': 'POLYGON',
            'name': 'name',
            'county': 'county',
            'type': 'type'
        }
        lm = LayerMapping(NeighborhoodV6, shp, db2shp, encoding='latin-1')
        kwargs = {'strict':True}
        if self.verbosity > 1:
            kwargs['verbose'] = True
        lm.save(**kwargs)

        # Correct the spelling of La Cañada, which often goes wrong.
        obj = NeighborhoodV6.objects.get(name__startswith='La Ca')
        obj.name = 'La Cañada Flintridge'
        obj.save()

        # Some extra metadata that's not in the shapes
        print "- Loading shape metadata"
        path = os.path.join(self.data_dir, 'metadata.csv')
        reader = unicodecsv.DictReader(open(path, 'r'))
        for row in reader:
            if self.verbosity > 1:
                print "-- %s" % row['Neighborhood']
            h = NeighborhoodV6.objects.get(name=row['Neighborhood'])
            h.slug = row['slug']
            h.square_miles = h.get_square_miles()
            h.has_statistics = int(row['Has stats'])
            h.simple_polygon_4326 = h.get_simple_polygon()
            h.save()