from django.core import mail
from django.urls import reverse
from rest_framework import status

from apps.utils.tests import DocgiTestCase


def parse_get_code(email_body: str) -> str:
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
        code = parse_get_code(get_code_email.body)

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
