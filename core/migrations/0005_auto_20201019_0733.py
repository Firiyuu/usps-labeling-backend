# Generated by Django 3.1.2 on 2020-10-19 07:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_auto_20201017_0225'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('customs_name', models.CharField(max_length=100)),
                ('customs_sku', models.CharField(max_length=100)),
                ('customs_description', models.CharField(max_length=100)),
                ('customs_quantity', models.CharField(max_length=100)),
                ('customs_amount', models.CharField(max_length=100)),
                ('customs_currency', models.CharField(max_length=100)),
                ('customs_country', models.CharField(max_length=100)),
                ('tariff_code', models.CharField(max_length=100)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'core_customs',
                'ordering': ['order'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.CharField(max_length=100)),
                ('price', models.CharField(max_length=100)),
                ('weight', models.CharField(max_length=100)),
                ('dimensions_length', models.CharField(max_length=100)),
                ('dimensions_width', models.CharField(max_length=100)),
                ('dimensions_depth', models.CharField(max_length=100)),
                ('dimensions_unit', models.CharField(max_length=100)),
                ('identical_package', models.IntegerField()),
                ('method', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'core_items',
                'ordering': ['order'],
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='packages',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('weight_unit', models.CharField(max_length=100)),
                ('company', models.CharField(max_length=100)),
                ('address1', models.CharField(max_length=100)),
                ('address2', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zipcode', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('is_archived', models.BooleanField(default=False)),
                ('custom_items', models.ManyToManyField(to='core.Customs')),
                ('line_items', models.ManyToManyField(to='core.Items')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'core_orders',
                'managed': True,
            },
        ),
    ]