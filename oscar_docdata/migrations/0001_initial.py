# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocdataOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('merchant_name', models.CharField(default=b'wakawakafoundation_org', max_length=100, verbose_name='Docdata account')),
                ('merchant_order_id', models.CharField(default=b'', max_length=100, verbose_name='Order ID')),
                ('order_key', models.CharField(default=b'', unique=True, max_length=200, verbose_name='Payment cluster ID')),
                ('status', models.CharField(default=b'new', max_length=50, verbose_name='Status', choices=[(b'new', 'New'), (b'in_progress', 'In Progress'), (b'pending', 'Pending'), (b'paid', 'Paid'), (b'paid_refunded', 'Paid, part refunded'), (b'cancelled', 'Cancelled'), (b'charged_back', 'Charged back'), (b'refunded', 'Refunded'), (b'expired', 'Expired'), (b'unknown', 'Unknown')])),
                ('language', models.CharField(default=b'en', max_length=5, verbose_name='Language', blank=True)),
                ('total_gross_amount', models.DecimalField(verbose_name='Total gross amount', max_digits=15, decimal_places=2)),
                ('currency', models.CharField(max_length=10, verbose_name='Currency')),
                ('country', models.CharField(max_length=2, null=True, verbose_name='Country_code', blank=True)),
                ('total_registered', models.DecimalField(default=Decimal('0.00'), verbose_name='Total registered', max_digits=15, decimal_places=2)),
                ('total_shopper_pending', models.DecimalField(default=Decimal('0.00'), verbose_name='Total shopper pending', max_digits=15, decimal_places=2)),
                ('total_acquirer_pending', models.DecimalField(default=Decimal('0.00'), verbose_name='Total acquirer pending', max_digits=15, decimal_places=2)),
                ('total_acquirer_approved', models.DecimalField(default=Decimal('0.00'), verbose_name='Total acquirer approved', max_digits=15, decimal_places=2)),
                ('total_captured', models.DecimalField(default=Decimal('0.00'), verbose_name='Total captured', max_digits=15, decimal_places=2)),
                ('total_refunded', models.DecimalField(default=Decimal('0.00'), verbose_name='Total refunded', max_digits=15, decimal_places=2)),
                ('total_charged_back', models.DecimalField(default=Decimal('0.00'), verbose_name='Total changed back', max_digits=15, decimal_places=2)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
            ],
            options={
                'ordering': ('-created', '-updated'),
                'verbose_name': 'Docdata Order',
                'verbose_name_plural': 'Docdata Orders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocdataPayment',
            fields=[
                ('payment_id', models.CharField(primary_key=True, default=b'', serialize=False, max_length=100, blank=True, verbose_name='Payment id')),
                ('status', models.CharField(default=b'NEW', max_length=30, verbose_name='status')),
                ('payment_method', models.CharField(default=b'', max_length=60, blank=True)),
                ('confidence_level', models.CharField(default=b'', verbose_name='Confidence level', max_length=30, editable=False)),
                ('amount_allocated', models.DecimalField(default=Decimal('0.00'), verbose_name='Amount Allocated', editable=False, max_digits=12, decimal_places=2)),
                ('amount_debited', models.DecimalField(default=Decimal('0.00'), verbose_name='Amount Debited', editable=False, max_digits=12, decimal_places=2)),
                ('amount_refunded', models.DecimalField(default=Decimal('0.00'), verbose_name='Amount Refunded', editable=False, max_digits=12, decimal_places=2)),
                ('amount_chargeback', models.DecimalField(default=Decimal('0.00'), verbose_name='Amount Changed back', editable=False, max_digits=12, decimal_places=2)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
            ],
            options={
                'ordering': ('payment_id',),
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocdataDirectDebitPayment',
            fields=[
                ('docdatapayment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='oscar_docdata.DocdataPayment')),
                ('holder_name', models.CharField(max_length=35)),
                ('holder_city', models.CharField(max_length=35)),
                ('holder_country_code', models.CharField(max_length=2, null=True, verbose_name='Country_code', blank=True)),
                ('iban', models.CharField(max_length=34)),
                ('bic', models.CharField(max_length=11)),
            ],
            options={
                'ordering': ('-created', '-updated'),
                'verbose_name': 'Direct Debit Payment',
                'verbose_name_plural': 'Derect Debit Payments',
            },
            bases=('oscar_docdata.docdatapayment',),
        ),
        migrations.AddField(
            model_name='docdatapayment',
            name='docdata_order',
            field=models.ForeignKey(related_name='payments', to='oscar_docdata.DocdataOrder'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='docdatapayment',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_oscar_docdata.docdatapayment_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]
