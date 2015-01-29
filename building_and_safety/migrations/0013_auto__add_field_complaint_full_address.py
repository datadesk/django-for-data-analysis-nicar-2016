# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Complaint.full_address'
        db.add_column(u'building_and_safety_complaint', 'full_address',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Complaint.full_address'
        db.delete_column(u'building_and_safety_complaint', 'full_address')


    models = {
        u'building_and_safety.complaint': {
            'Meta': {'ordering': "('-date_received',)", 'object_name': 'Complaint'},
            'address_house_fraction': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'address_house_number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'address_street_direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'address_street_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address_street_suffix': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'address_street_suffix_direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'address_street_zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'area_planning_commission': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'case_flag': ('django.db.models.fields.BooleanField', [], {}),
            'case_number_csr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'csr': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'csr_priority': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'csr_problem_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_closed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_due': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_received': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'days_since_complaint': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'full_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gis_pin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {}),
            'ladbs_inspection_district': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'lat_long': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'more_than_one_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'neighborhoodv6': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building_and_safety.NeighborhoodV6']", 'null': 'True', 'blank': 'True'}),
            'point_4326': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'response_days': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        u'building_and_safety.neighborhoodv6': {
            'Meta': {'ordering': "('name',)", 'object_name': 'NeighborhoodV6'},
            'avg_days_to_response': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'closed_complaints': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'closed_over_one_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'density': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'has_statistics': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'open_complaints': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'open_over_one_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'percent_over_one_year_to_response': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'polygon_4326': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'population': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'population_source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'population_source_explainer': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'square_feet': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'square_miles': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'total_complaints': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_unresolved_after_one_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'unclassified'", 'max_length': '300'})
        }
    }

    complete_apps = ['building_and_safety']