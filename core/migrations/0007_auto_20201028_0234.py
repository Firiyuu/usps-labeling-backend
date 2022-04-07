# Generated by Django 3.1.2 on 2020-10-27 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_merge_20201028_0234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='items',
            name='user',
        ),
        migrations.AddField(
            model_name='labels',
            name='is_international',
            field=models.BooleanField(default=False),
        ),
    ]
