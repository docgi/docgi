from rest_framework import routers

from . import apps, apis

app_name = apps.KanbanConfig.name


router = routers.DefaultRouter()

router.register(
    r"boards",
    apis.BoardViewSet,
    basename="boards"
)

router.register(
    r"board-columns",
    apis.BoarColumnViewSet,
    basename="board-columns"
)

router.register(
    r"tasks",
    apis.TaskViewSet,
    basename="tasks"
)

urlpatterns = [

]

urlpatterns += router.urls
