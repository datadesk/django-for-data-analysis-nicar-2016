# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Complaint'
        db.create_table(u'building_and_safety_complaint', (
            ('csr', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_index=True)),
            ('ladbs_inspection_district', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('address_house_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('address_house_fraction', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('address_street_direction', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('address_street_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('address_street_suffix', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('address_street_suffix_direction', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('address_street_zip', self.gf('django.db.models.fields.IntegerField')()),
            ('date_received', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('date_closed', self.gf('django.db.models.fields.DateField')(null=True)),
            ('date_due', self.gf('django.db.models.fields.DateField')()),
            ('case_flag', self.gf('django.db.models.fields.BooleanField')()),
            ('csr_priority', self.gf('django.db.models.fields.IntegerField')()),
            ('gis_pin', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('csr_problem_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('area_planning_commission', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('case_number_csr', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('response_days', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('lat_long', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('point_4326', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'building_and_safety', ['Complaint'])

        # Adding model 'NeighborhoodV6'
        db.create_table(u'building_and_safety_neighborhoodv6', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('has_statistics', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('population', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('population_source', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('population_source_explainer', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(default='unclassified', max_length=300)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('square_miles', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('square_feet', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('density', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('polygon_4326', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'building_and_safety', ['NeighborhoodV6'])


    def backwards(self, orm):
        # Deleting model 'Complaint'
        db.delete_table(u'building_and_safety_complaint')

        # Deleting model 'NeighborhoodV6'
        db.delete_table(u'building_and_safety_neighborhoodv6')


    models = {
        u'building_and_safety.complaint': {
            'Meta': {'ordering': "('-date_received',)", 'object_name': 'Complaint'},
            'address_house_fraction': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'address_house_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'address_street_direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'address_street_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address_street_suffix': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'address_street_suffix_direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'address_street_zip': ('django.db.models.fields.IntegerField', [], {}),
            'area_planning_commission': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'case_flag': ('django.db.models.fields.BooleanField', [], {}),
            'case_number_csr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'csr': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_index': 'True'}),
            'csr_priority': ('django.db.models.fields.IntegerField', [], {}),
            'csr_problem_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_closed': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_due': ('django.db.models.fields.DateField', [], {}),
            'date_received': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'gis_pin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {}),
            'ladbs_inspection_district': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'lat_long': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'point_4326': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'response_days': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'building_and_safety.neighborhoodv6': {
            'Meta': {'ordering': "('name',)", 'object_name': 'NeighborhoodV6'},
            'county': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'density': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'has_statistics': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'polygon_4326': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'population': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'population_source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'population_source_explainer': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'square_feet': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'square_miles': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'unclassified'", 'max_length': '300'})
        }
    }

    complete_apps = ['building_and_safety']