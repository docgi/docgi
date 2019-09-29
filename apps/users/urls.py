from django.urls import path
from rest_framework import routers

from . import apis, apps


app_name = apps.UsersConfig.name

router = routers.DefaultRouter()

router.register(
    r"",
    apis.UserViewSet,
    basename="users"
)

urlpatterns = [

]

urlpatterns += router.urls
