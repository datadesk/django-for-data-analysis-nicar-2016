# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Complaint'
        db.create_table(u'building_and_safety_complaint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('csr', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('ladbs_inspection_district', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('address_house_number', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('address_house_fraction', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('address_street_direction', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('address_street_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('address_street_suffix', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('address_street_suffix_direction', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('address_street_zip', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('date_received', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_closed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_due', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('case_flag', self.gf('django.db.models.fields.BooleanField')()),
            ('csr_priority', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('gis_pin', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('csr_problem_type', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('area_planning_commission', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('case_number_csr', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('response_days', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('lon', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('full_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')()),
            ('gt_30_days', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gt_90_days', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gt_180_days', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('more_than_one_year', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('days_since_complaint', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('past_due_date', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('days_past_due_date', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('inspector', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('inspector_phone_number', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('lat_visited', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('investigate_further', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('housing_dept_related', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'building_and_safety', ['Complaint'])


    def backwards(self, orm):
        # Deleting model 'Complaint'
        db.delete_table(u'building_and_safety_complaint')


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
            'days_past_due_date': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'days_since_complaint': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'full_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gis_pin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'gt_180_days': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gt_30_days': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gt_90_days': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'housing_dept_related': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inspector': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'inspector_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'investigate_further': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {}),
            'ladbs_inspection_district': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lat_visited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'more_than_one_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'past_due_date': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'response_days': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['building_and_safety']