# Generated by Django 2.2.5 on 2019-10-19 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0002_auto_20191017_0417'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='activate',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]