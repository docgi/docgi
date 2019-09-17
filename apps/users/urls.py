from rest_framework import routers

from . import apis


router = routers.DefaultRouter()

router.register(
    r"users",
    apis.UserViewSet,
    basename="users"
)

urlpatterns = [

]

urlpatterns += router.urls
