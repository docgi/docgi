# Generated by Django 3.0.6 on 2020-05-15 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_auto_20200515_1023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='draft',
            field=models.BooleanField(default=False),
        ),
    ]