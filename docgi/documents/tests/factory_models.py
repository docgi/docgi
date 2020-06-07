import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from .. import models
from ...users.tests.factories_models import UserFactory
from ...workspaces.tests.factory_models import WorkspaceFactory

User = get_user_model()


class CollectionFactory(DjangoModelFactory):
    class Meta:
        model = models.Collection

    workspace = factory.SubFactory(WorkspaceFactory)
    creator = factory.SubFactory(UserFactory)
    name = fuzzy.FuzzyText(prefix="collection_")


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = models.Document

    name = fuzzy.FuzzyText(prefix="document_")
    collection = factory.SubFactory(CollectionFactory)
    creator = factory.SubFactory(UserFactory)

