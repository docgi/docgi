from django.urls import path

from .apis import DocgiTokenObtainPairView


app_name = "auth"

urlpatterns = [
    path("auth/login/", DocgiTokenObtainPairView.as_view(), name='login'),
]
