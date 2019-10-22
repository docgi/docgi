from django.urls import path

from .apis import DocgiTokenObtainPairView


app_name = "authentication"

urlpatterns = [
    path("auth/login/", DocgiTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
