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
    r"docs",
    apis.DocumentViewSet,
    basename="documents"
)

urlpatterns = []
urlpatterns += router.urls
