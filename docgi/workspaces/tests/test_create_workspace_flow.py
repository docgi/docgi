from django.core import mail
from django.urls import reverse
from rest_framework import status

from docgi.base.tests import DocgiTestCase


def parse_email_get_code(email_body: str) -> str:
    """
    Parse get code email and return only code for create workspace.
    """
    return email_body


class TestCreateWorkSpaceFlow(DocgiTestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_flow(self):
        # Step 1: Get code.
        url_get_code = reverse("workspaces:create-workspace-get-code")
        payload = {
            "email": self._creator_email
        }
        self.post(path=url_get_code, data=payload, status_code=status.HTTP_200_OK)
        get_code_email = mail.outbox.pop()
        code = parse_email_get_code(get_code_email.body)

        # Step 2: Check code.
        payload.update(code=code)
        url_check_code = reverse("workspaces:create-workspace-check-code")
        self.post(path=url_check_code, data=payload, status_code=status.HTTP_200_OK)

        # Step 3: Put all together and create workspace.
        payload.update(workspace_name=self._workspace_name)
        url_create_workspace = reverse("workspaces:create-workspace-create-workspace")
        res = self.post(path=url_create_workspace, data=payload)
        self.assertIsNotNone(res.data["token"])
        self.assertIsNotNone(res.data["user"])
        self.assertTrue(res.data["user"]["need_pass"])

        # Step 4: After create, set password for user
        token = res.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url_set_pass = reverse("users:user-set-password")
        password = "123123123"

        # First, test with wrong case
        payload = {
            "password": password,
            "confirm_password": password + "1"
        }
        self.post(url_set_pass, data=payload, status_code=status.HTTP_400_BAD_REQUEST)

        # Then happy case
        payload = {
            "password": password,
            "confirm_password": password
        }
        res = self.post(url_set_pass, data=payload, status_code=status.HTTP_200_OK)
        self.assertIsNotNone(res.data["user"])
        self.assertEqual(res.data["workspace_name"], self._workspace_name)

    def test_flow_create_with_uppercase(self):
        # Step 1: Get code.
        url_get_code = reverse("workspaces:create-workspace-get-code")
        payload = {
            "email": self._creator_email
        }
        self.post(path=url_get_code, data=payload, status_code=status.HTTP_200_OK)
        get_code_email = mail.outbox.pop()
        code = parse_email_get_code(get_code_email.body)

        # Step 2: Check code.
        payload.update(code=code)
        url_check_code = reverse("workspaces:create-workspace-check-code")
        self.post(path=url_check_code, data=payload, status_code=status.HTTP_200_OK)

        # Step 3: Put all together and create workspace.
        workspace_name = "WORKSPACE"
        payload.update(workspace_name=workspace_name)
        url_create_workspace = reverse("workspaces:create-workspace-create-workspace")
        res = self.post(path=url_create_workspace, data=payload)
        self.assertIsNotNone(res.data["token"])
        self.assertIsNotNone(res.data["user"])
        self.assertTrue(res.data["user"]["need_pass"])
        self.assertEqual(res.data["workspace"]["name"], workspace_name.lower())

        # Validate in database
        from docgi.workspaces.models import Workspace
        exist = Workspace.objects.filter(name=workspace_name.lower()).exists()
        self.assertTrue(exist)

        not_exist = Workspace.objects.filter(name=workspace_name).exists()
        self.assertFalse(not_exist)
