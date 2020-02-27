import json

from django.contrib.auth import get_user_model
from django.test.client import encode_multipart
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.workspaces.models import Workspace, WorkspaceMember

User = get_user_model()
JSON_CONTENT = "application/json"
BOUNDARY = "BoUnDaRyStRiNg"
MULTIPART_CONTENT = "multipart/form-data; boundary=%s" % BOUNDARY


class DocgiTestCase(APITestCase):
    _workspace_name = "docgi-workspace"
    _creator_email = "workspace-creator@email.com"
    _creator_username = "creator"
    _password = "123456@abc"

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

        cls.member1 = User.objects.create_user(
            email="u1@email.com",
            username="u1",
            password=cls._password
        )
        cls.member2 = User.objects.create_user(
            email="u2@email.com",
            username="u2",
            password=cls._password
        )
        cls.member3 = User.objects.create_user(
            email="u3@email.com",
            username="u3",
            password=cls._password
        )
        cls.member4 = User.objects.create_user(
            email="u4@email.com",
            username="u4",
            password=cls._password
        )
        for user in [cls.member1, cls.member2, cls.member3, cls.member4]:
            cls.workspace.members.create(user=user,
                                         workspace=cls.workspace,
                                         role=WorkspaceMember.MemberRole.MEMBER.value)

    def setUp(self) -> None:
        self.make_login(self.creator)

    def tearDown(self) -> None:
        self.make_logout()

    @staticmethod
    def _encode_data(data, content_type):
        if data is None or data == "":
            return data

        if content_type is JSON_CONTENT and isinstance(data, (list, dict, tuple)):
            return json.dumps(data)

        if content_type is MULTIPART_CONTENT:
            return encode_multipart(
                boundary=BOUNDARY,
                data=data
            )

        return data

    def make_login(self, user: User):
        """
        This function make login and set valid `token`.
        By default login with creator of workspace.
        """
        payload_login = {
            "workspace": self._workspace_name,
            "email": user.email,
            "password": self._password
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

    def post(self, path, data=None, format=None, content_type=JSON_CONTENT,
             follow=False, status_code=status.HTTP_201_CREATED, **kwargs):
        post_data = self._encode_data(data=data, content_type=content_type)
        res = self.client.post(path=path,
                               data=post_data,
                               format=format,
                               content_type=content_type,
                               follow=follow,
                               **kwargs)
        self.assertEqual(res.status_code, status_code, res.data)
        return res

    def put(self, path, data="", content_type=JSON_CONTENT,
            follow=False, secure=False, status_code=status.HTTP_200_OK, **kwargs):
        put_data = self._encode_data(data=data, content_type=content_type)
        res = self.client.put(path=path,
                              data=put_data,
                              content_type=content_type,
                              follow=follow,
                              secure=secure,
                              **kwargs)
        self.assertEqual(res.status_code, status_code, res.data)
        return res

    def patch(self, path, data="", content_type=JSON_CONTENT,
              follow=False, secure=False, status_code=status.HTTP_200_OK, **kwargs):
        patch_data = self._encode_data(data=data, content_type=content_type)
        res = self.client.patch(path=path,
                                data=patch_data,
                                content_type=content_type,
                                follow=follow,
                                secure=secure,
                                **kwargs)
        self.assertEqual(res.status_code, status_code, res.data)
        return res

    def delete(self, path, data="", content_type=JSON_CONTENT,
               follow=False, secure=False, status_code=status.HTTP_204_NO_CONTENT, **kwargs):
        delete_data = self._encode_data(data=data, content_type=content_type)
        res = self.client.delete(path=path,
                                 data=delete_data,
                                 content_type=content_type,
                                 follow=follow,
                                 secure=secure,
                                 **kwargs)
        self.assertEqual(res.status_code, status_code, res.data)
        return res
