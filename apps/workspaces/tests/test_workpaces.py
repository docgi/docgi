from django.urls import reverse
from rest_framework import status

from apps.utils.tests import DocgiTestCase


class TestWorkspace(DocgiTestCase):
    def test_get_workspace_info(self):
        url_workspace = reverse("workspace:workspace-info")
        self.get(url_workspace)
        self.make_logout()
        self.get(url_workspace, status_code=status.HTTP_401_UNAUTHORIZED)
