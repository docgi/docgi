from rest_framework import routers

from . import apps, apis


router = routers.DefaultRouter()

router.register(
    r"users",
    apis.UserViewSet,
    basename="users"
)

urlpatterns = [

]

urlpatterns += router.urls
