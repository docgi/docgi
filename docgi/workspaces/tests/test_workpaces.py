from django.urls import reverse
from rest_framework import status

from docgi.base.tests import DocgiTestCase, MULTIPART_CONTENT


class TestWorkspace(DocgiTestCase):
    url_workspace = reverse("workspaces:workspace-info")

    def test_check_workspace_exist(self):
        url_check_workspace = reverse("workspaces:check")
        self.make_logout()
        payload = {
            "name": self.workspace.name
        }
        res = self.post(url_check_workspace, data=payload, status_code=status.HTTP_200_OK)
        self.assertTrue(res.data["exist"])
        self.assertIsNotNone(res.data["workspace"])

    def test_check_workspace_not_exist(self):
        url_check_workspace = reverse("workspaces:check")
        self.make_logout()
        payload = {
            "name": "not-exist"
        }
        res = self.post(url_check_workspace, data=payload, status_code=status.HTTP_200_OK)
        self.assertFalse(res.data["exist"])
        self.assertIsNone(res.data["workspace"])

    def test_get_workspace_info(self):
        self.get(self.url_workspace)
        self.make_logout()
        self.get(self.url_workspace, status_code=status.HTTP_401_UNAUTHORIZED)

    def test_update_logo(self):
        with open("test_fixtures/meow.jpg", "rb") as f:
            payload = {
                "logo": f
            }
            res = self.put(self.url_workspace,
                           data=payload, status_code=status.HTTP_200_OK,
                           content_type=MULTIPART_CONTENT)
            self.assertIsNotNone(res.data["logo"])

    def test_update_workspace_name(self):
        new_name = self.workspace.name + "new-name"
        payload = {
            "name": new_name
        }
        res = self.put(self.url_workspace,
                       data=payload, status_code=status.HTTP_200_OK, content_type=MULTIPART_CONTENT)
        self.assertEqual(res.data["name"], self.workspace.name)
