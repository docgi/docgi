from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.workspaces.models import Workspace, WorkspaceMember

User = get_user_model()


class DocgiTestCase(APITestCase):
    _workspace_name = "docgi-workspace"
    _password = "123456@abc"
    _creator_email = "workspace-creator@email.com"
    _creator_username = "creator"

    token = None
    creator: User
    workspace: Workspace

    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create_user(
            email=cls._creator_email,
            username=cls._creator_username,
            password=cls._password
        )

        cls.workspace = Workspace.objects.create(name=cls._workspace_name,
                                                 creator=cls.creator)
        cls.workspace.members.create(user=cls.creator,
                                     workspace=cls.workspace,
                                     role=WorkspaceMember.MemberRole.ADMIN.value)

    def tearDown(self) -> None:
        self.make_logout()

    def setUp(self) -> None:
        self.make_login()

    def make_login(self, email=_creator_email, password=_password):
        """
        This function make login and set valid `token`.
        """
        payload_login = {
            "workspace": self._workspace_name,
            "email": email,
            "password": password
        }
        url_login = reverse("authentication:login")
        res = self.post(url_login, data=payload_login, status_code=status.HTTP_200_OK)
        self.token = res.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def make_logout(self):
        self.client.credentials()

    def get(self, path, data=None, follow=False, status_code=status.HTTP_200_OK, **kwargs):
        res = self.client.get(path=path,
                              data=data,
                              follow=follow,
                              **kwargs)
        self.assertEqual(res.status_code, status_code, res.data)
        return res

    def post(self, path, data=None, format=None, content_type=None,
             follow=False, status_code=status.HTTP_201_CREATED, **kwargs):
        res = self.client.post(path=path,
                               data=data,
                               format=format,
                               content_type=content_type,
                               follow=follow,
                               **kwargs)
        self.assertEqual(res.status_code, status_code, res.data)
        return res
