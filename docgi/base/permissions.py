from django.contrib.auth import get_user_model
from rest_framework.request import Request

User = get_user_model()

POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
GET = "GET"
DELETE = "DELETE"


class DocgiPermissionHelper(object):
    @staticmethod
    def is_put(request: Request) -> bool:
        return request.method == PUT

    @staticmethod
    def is_patch(request: Request) -> bool:
        return request.method == PATCH

    @staticmethod
    def is_update(request: Request) -> bool:
        return DocgiPermissionHelper.is_patch(request) | DocgiPermissionHelper.is_put(request)

    @staticmethod
    def is_delete(request: Request) -> bool:
        return request.method == DELETE

    @staticmethod
    def is_workspace_admin(user: User) -> bool:
        return user.is_workspace_admin()
