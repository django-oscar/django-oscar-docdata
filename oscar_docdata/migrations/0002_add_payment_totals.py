# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DocdataPayment.confidence_level'
        db.add_column(u'oscar_docdata_docdatapayment', 'confidence_level',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)

        # Adding field 'DocdataPayment.amount_allocated'
        db.add_column(u'oscar_docdata_docdatapayment', 'amount_allocated',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataPayment.amount_debited'
        db.add_column(u'oscar_docdata_docdatapayment', 'amount_debited',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataPayment.amount_refunded'
        db.add_column(u'oscar_docdata_docdatapayment', 'amount_refunded',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataPayment.amount_chargeback'
        db.add_column(u'oscar_docdata_docdatapayment', 'amount_chargeback',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataOrder.total_registered'
        db.add_column(u'oscar_docdata_docdataorder', 'total_registered',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=15, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataOrder.total_shopper_pending'
        db.add_column(u'oscar_docdata_docdataorder', 'total_shopper_pending',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=15, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataOrder.total_acquirer_pending'
        db.add_column(u'oscar_docdata_docdataorder', 'total_acquirer_pending',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=15, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataOrder.total_acquirer_approved'
        db.add_column(u'oscar_docdata_docdataorder', 'total_acquirer_approved',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=15, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataOrder.total_captured'
        db.add_column(u'oscar_docdata_docdataorder', 'total_captured',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=15, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataOrder.total_refunded'
        db.add_column(u'oscar_docdata_docdataorder', 'total_refunded',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=15, decimal_places=2),
                      keep_default=False)

        # Adding field 'DocdataOrder.total_charged_back'
        db.add_column(u'oscar_docdata_docdataorder', 'total_charged_back',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=15, decimal_places=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DocdataPayment.confidence_level'
        db.delete_column(u'oscar_docdata_docdatapayment', 'confidence_level')

        # Deleting field 'DocdataPayment.amount_allocated'
        db.delete_column(u'oscar_docdata_docdatapayment', 'amount_allocated')

        # Deleting field 'DocdataPayment.amount_debited'
        db.delete_column(u'oscar_docdata_docdatapayment', 'amount_debited')

        # Deleting field 'DocdataPayment.amount_refunded'
        db.delete_column(u'oscar_docdata_docdatapayment', 'amount_refunded')

        # Deleting field 'DocdataPayment.amount_chargeback'
        db.delete_column(u'oscar_docdata_docdatapayment', 'amount_chargeback')

        # Deleting field 'DocdataOrder.total_registered'
        db.delete_column(u'oscar_docdata_docdataorder', 'total_registered')

        # Deleting field 'DocdataOrder.total_shopper_pending'
        db.delete_column(u'oscar_docdata_docdataorder', 'total_shopper_pending')

        # Deleting field 'DocdataOrder.total_acquirer_pending'
        db.delete_column(u'oscar_docdata_docdataorder', 'total_acquirer_pending')

        # Deleting field 'DocdataOrder.total_acquirer_approved'
        db.delete_column(u'oscar_docdata_docdataorder', 'total_acquirer_approved')

        # Deleting field 'DocdataOrder.total_captured'
        db.delete_column(u'oscar_docdata_docdataorder', 'total_captured')

        # Deleting field 'DocdataOrder.total_refunded'
        db.delete_column(u'oscar_docdata_docdataorder', 'total_refunded')

        # Deleting field 'DocdataOrder.total_charged_back'
        db.delete_column(u'oscar_docdata_docdataorder', 'total_charged_back')


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
            'merchant_order_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'order_key': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '50'}),
            'total_acquirer_approved': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_acquirer_pending': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_captured': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_charged_back': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_gross_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_refunded': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_registered': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_shopper_pending': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'oscar_docdata.docdatapayment': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocdataPayment'},
            'amount_allocated': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'amount_chargeback': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'amount_debited': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'amount_refunded': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'confidence_level': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
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