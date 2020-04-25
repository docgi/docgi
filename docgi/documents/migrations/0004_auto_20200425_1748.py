# Generated by Django 3.0.3 on 2020-04-25 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_remove_collection_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='emoji',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='collection',
            unique_together=set(),
        ),
    ]
