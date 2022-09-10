from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    LeaderBoardView,
    LoginView,
    QuestionsView,
    QuestionView,
    RegisterView,
    VerifyView,
    UserView,
    LogoutView,
    ForgotPasswordView,
    PasswordTokenCheckView,
    SetNewPasswordView,
    ChangePasswordView,
)


urlpatterns = [
    path("register", RegisterView.as_view()),
    path("verify-email/", VerifyView.as_view(), name="verify-email"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("user/", UserView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordTokenCheckView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete",
        SetNewPasswordView.as_view(),
        name="password-reset-complete",
    ),
    path("change-password", ChangePasswordView.as_view(), name="change-password"),
    path("question/", QuestionsView.as_view()),
    path("question/<qstn_id>", QuestionView.as_view()),
    path("leaderboard/", LeaderBoardView.as_view()),
]
