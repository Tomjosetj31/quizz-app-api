from django.urls import path

from .views import LoginView, RegisterView, VerifyView


urlpatterns = [
    path("register", RegisterView.as_view()),
    path("verify-email/", VerifyView.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="login"),
]
