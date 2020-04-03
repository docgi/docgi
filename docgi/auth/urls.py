from django.urls import path

from . import apis


app_name = "auth"

urlpatterns = [
    path("auth/login/", apis.DocgiTokenObtainPairView.as_view(), name="login"),
    path("auth/forgot-password/", apis.DocgiForgotPassword.as_view(), name="forgot-password"),
    path("auth/reset-password/", apis.DocgiResetPassword.as_view(), name="reset-password"),
]
