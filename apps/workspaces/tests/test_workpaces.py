from django.urls import reverse
from rest_framework import status

from apps.utils.tests import DocgiTestCase


class TestWorkspace(DocgiTestCase):
    def setUp(self) -> None:
        self.make_login()

    def test_get_workspace_info(self):
        url_workspace = reverse("workspace:workspace-info")
        res = self.get(url_workspace)
