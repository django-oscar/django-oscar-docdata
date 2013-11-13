# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocdataOrder'
        db.create_table(u'oscar_docdata_docdataorder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('merchant_order_id', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('order_key', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=200, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=50)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=5, blank=True)),
            ('total_gross_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'oscar_docdata', ['DocdataOrder'])

        # Adding model 'DocdataPayment'
        db.create_table(u'oscar_docdata_docdatapayment', (
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_oscar_docdata.docdatapayment_set', null=True, to=orm['contenttypes.ContentType'])),
            ('docdata_order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['oscar_docdata.DocdataOrder'])),
            ('payment_id', self.gf('django.db.models.fields.CharField')(default='', max_length=100, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='NEW', max_length=30)),
            ('payment_method', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'oscar_docdata', ['DocdataPayment'])

        # Adding model 'DocdataDirectDebitPayment'
        db.create_table(u'oscar_docdata_docdatadirectdebitpayment', (
            (u'docdatapayment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oscar_docdata.DocdataPayment'], unique=True, primary_key=True)),
            ('holder_name', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('holder_city', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('holder_country_code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('iban', self.gf('django.db.models.fields.CharField')(max_length=34)),
            ('bic', self.gf('django.db.models.fields.CharField')(max_length=11)),
        ))
        db.send_create_signal(u'oscar_docdata', ['DocdataDirectDebitPayment'])


    def backwards(self, orm):
        # Deleting model 'DocdataOrder'
        db.delete_table(u'oscar_docdata_docdataorder')

        # Deleting model 'DocdataPayment'
        db.delete_table(u'oscar_docdata_docdatapayment')

        # Deleting model 'DocdataDirectDebitPayment'
        db.delete_table(u'oscar_docdata_docdatadirectdebitpayment')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'oscar_docdata.docdatadirectdebitpayment': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocdataDirectDebitPayment', '_ormbases': [u'oscar_docdata.DocdataPayment']},
            'bic': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            u'docdatapayment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oscar_docdata.DocdataPayment']", 'unique': 'True', 'primary_key': 'True'}),
            'holder_city': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'holder_country_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'holder_name': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '34'})
        },
        u'oscar_docdata.docdataorder': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocdataOrder'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '5', 'blank': 'True'}),
            'merchant_order_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'order_key': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '50'}),
            'total_gross_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'oscar_docdata.docdatapayment': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocdataPayment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'docdata_order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['oscar_docdata.DocdataOrder']"}),
            'payment_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'primary_key': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_oscar_docdata.docdatapayment_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '30'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['oscar_docdata']