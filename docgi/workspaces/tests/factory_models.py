import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from ...users.tests.factories_models import UserFactory
from .. import models


User = get_user_model()


class WorkspaceFactory(DjangoModelFactory):
    class Meta:
        model = models.Workspace

    creator = factory.SubFactory(UserFactory)
    name = fuzzy.FuzzyText(prefix="workspace_", length=10)


class WorkspaceMemberFactory(DjangoModelFactory):
    class Meta:
        model = models.WorkspaceMember

    workspace = factory.SubFactory(WorkspaceFactory)
    user = factory.SubFactory(UserFactory)
    role = fuzzy.FuzzyChoice(models.WorkspaceMember.WorkspaceMemberRole.to_choices(),
                             getter=lambda role: role[0])
