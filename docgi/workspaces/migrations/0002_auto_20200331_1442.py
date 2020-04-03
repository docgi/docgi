# Generated by Django 3.0.3 on 2020-03-31 14:42

import django.core.files.storage
from django.db import migrations
import docgi.workspaces.models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workspace',
            name='logo',
            field=imagekit.models.fields.ProcessedImageField(blank=True, default='', storage=django.core.files.storage.FileSystemStorage(), upload_to=docgi.workspaces.models.Workspace.logo_path),
            preserve_default=False,
        ),
    ]
