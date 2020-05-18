from rest_framework import routers

from . import apps, apis


app_name = apps.DocumentsConfig.name
router = routers.DefaultRouter()

router.register(
    "collections",
    apis.CollectionViewSet,
    basename="collections"
)

router.register(
    r"documents",
    apis.DocumentViewSet,
    basename="documents"
)

router.register(
    r"document-images",
    apis.DocumentImageViewSet,
    basename="document-images"
)

urlpatterns = []
urlpatterns += router.urls
