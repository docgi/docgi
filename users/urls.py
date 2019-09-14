from rest_framework import routers

from . import apps, apis


router = routers.DefaultRouter()

router.register(
    r"",
    apis.UserViewSet,
    basename="users"
)

urlpatterns = [

]

urlpatterns += router.urls
