from factory import fuzzy
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = fuzzy.FuzzyText()
    email = fuzzy.FuzzyText(suffix="@email.com")
