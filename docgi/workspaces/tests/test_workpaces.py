from django.urls import reverse
from django.core import mail
from rest_framework import status

from docgi.base.tests import DocgiTestCase, MULTIPART_CONTENT
from docgi.workspaces.models import WorkspaceMember

url_send_invitation = reverse("workspaces:send-invitation")


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

    def test_make_sure_workspace_name_can_not_modify(self):
        new_name = self.workspace.name + "new-name"
        payload = {
            "name": new_name
        }
        res = self.put(self.url_workspace,
                       data=payload, status_code=status.HTTP_200_OK, content_type=MULTIPART_CONTENT)
        self.assertEqual(res.data["name"], self.workspace.name)


class TestInvitation(DocgiTestCase):
    def test_send_invitations_duplicate_email(self):
        payload = {
            "invitations": [
                {
                    "email": "1@email.com"
                },
                {
                    "email": "1@email.com",
                    "role": WorkspaceMember.MemberRole.ADMIN.value
                }
            ]
        }
        self.post(url_send_invitation, data=payload, status_code=status.HTTP_400_BAD_REQUEST)

    def test_send_invitations_invalid_email(self):
        payload = {
            "invitations": [
                {
                    "email": "@email.com"
                }
            ]
        }
        self.post(url_send_invitation, data=payload, status_code=status.HTTP_400_BAD_REQUEST)

    def test_send_invitations(self):
        payload = {
            "invitations": [
                {
                    "email": "1@email.com"
                },
                {
                    "email": "12@email.com"
                },
            ]
        }
        res = self.post(url_send_invitation, data=payload)
        self.assertEqual(len(res.data["recently_invited"]), 2)
        self.assertEqual(len(mail.outbox), 2)

    def test_make_sure_dont_resend(self):
        payload = {
            "invitations": [
                {
                    "email": "1@email.com"
                },
                {
                    "email": "12@email.com"
                },
            ]
        }
        res = self.post(url_send_invitation, data=payload)
        self.assertEqual(len(res.data["recently_invited"]), 2)
        self.assertEqual(len(mail.outbox), 2)

        res = self.post(url_send_invitation, data=payload)
        self.assertEqual(len(res.data["invited"]), 2)
        self.assertEqual(len(mail.outbox), 2)

    def test_invite_one_email_two_role(self):
        payload = {
            "invitations": [
                {
                    "email": "1@email.com",
                    "role": WorkspaceMember.MemberRole.MEMBER.value
                },
                {
                    "email": "1@email.com",
                    "role": WorkspaceMember.MemberRole.ADMIN.value
                }
            ]
        }
        self.post(url_send_invitation, data=payload, status_code=status.HTTP_400_BAD_REQUEST)

    def test_make_sure_dont_send_for_already_member(self):
        payload = {
            "invitations": [
                {
                    "email": "1@email.com"
                },
                {
                    "email": "12@email.com"
                },
                {
                    "email": self.member1.email
                },
                {
                    "email": self.member2.email
                },
                {
                    "email": self.member3.email
                },
                {
                    "email": self.member4.email
                },
            ]
        }
        res = self.post(url_send_invitation, data=payload)
        self.assertEqual(len(res.data["recently_invited"]), 2)
        self.assertEqual(len(mail.outbox), 2)
