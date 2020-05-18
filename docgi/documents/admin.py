from django.contrib import admin

from . import models


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "name", "workspace", "creator",
    )


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "name", "collection", "creator",
    )


@admin.register(models.DocumentImage)
class DocumentImageAdmin(admin.ModelAdmin):
    list_display = (
        "workspace", "image"
    )
