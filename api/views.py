import jwt
import datetime
import json

from .utils import Util, CustomerAccessPermission
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.core import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import (
    UserSerializer,
    LoginSerializer,
    UpdateUserSerializer,
    QuestionSerializer,
    LeaderBoardSerializer,
)
from .models import LeaderBoard, Question, User, Token


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data["email"])

        token = RefreshToken.for_user(user).access_token
        relative_link = reverse("verify-email")
        current_site = get_current_site(request).domain
        absolute_url = "http://" + current_site + relative_link + "?token=" + str(token)

        print(absolute_url)
        email_body = "Hi Use link below to verify your email \n" + absolute_url
        data = {"body": email_body, "subject": "verify your email", "to": user.email}
        Util.send_email(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyView(APIView):
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.verified_at = datetime.datetime.now()
                user.is_active = True
                user.save()

            return render(
                request,
                "app/success.html",
                {"message": "successfully verified your email"},
            )

        except jwt.ExpiredSignatureError as identifier:
            return render(
                request,
                "app/failure.html",
                {"message": "activation link expired"},
                status=400,
            )
        except jwt.exceptions.DecodeError as identifier:
            return render(
                request, "app/failure.html", {"message": "invalid token"}, status=401
            )


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = [CustomerAccessPermission]

    def get(self, request):
        instance = User.objects.get(id=request.user.id)
        serializer = UpdateUserSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        instance = User.objects.get(id=request.user.id)
        data = request.data
        serializer = UpdateUserSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request):
        instance = User.objects.get(id=request.user.id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = [CustomerAccessPermission]

    def delete(self, request):
        access_token = request.headers.get("Authorization").split(" ")[1]
        instance = Token.objects.get(access_token=access_token)
        instance.delete()

        return Response({"message": "success"}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data["email"]
        if not User.objects.filter(email=email).exists():
            return Response(
                {"message": "user didn't exist"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(email=email)
        user_id = user.id
        user_id_bytes = user_id.to_bytes(4, "little")
        uidb64 = urlsafe_base64_encode(user_id_bytes)

        token = PasswordResetTokenGenerator().make_token(user)
        relative_link = reverse(
            "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        current_site = get_current_site(request=request).domain
        absolute_url = "http://" + current_site + relative_link

        email_body = "Hi Use link below to reset your password \n" + absolute_url
        data = {"body": email_body, "subject": "reset your password", "to": user.email}
        Util.send_email(data)
        return Response(
            {"message": "password reset link sent to your registered email address"},
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckView(APIView):
    def get(self, request, uidb64, token):
        try:
            user_id_byte = urlsafe_base64_decode(uidb64)
            user_id_int = int.from_bytes(user_id_byte, "little")

            id = smart_str(user_id_int)
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return render(
                    request,
                    "app/failure.html",
                    {"message": "invalid token, request new link"},
                    status=401,
                )

            return render(
                request,
                "app/password_reset.html",
                {"token": token, "uidb64": uidb64},
                status=200,
            )

        except DjangoUnicodeDecodeError as identifier:
            return render(
                request,
                "app/failure.html",
                {"message": "invalid token, request new link"},
                status=401,
            )


class SetNewPasswordView(APIView):
    def post(self, request):
        uidb64 = request.data["uidb64"]
        token = request.data["token"]
        password = request.data["password"]

        try:
            user_id_byte = urlsafe_base64_decode(uidb64)
            user_id_int = int.from_bytes(user_id_byte, "little")

            id = smart_str(user_id_int)
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return render(
                    request,
                    "app/failure.html",
                    {"message": "invalid token, request new link"},
                    status=401,
                )
            user.set_password(password)
            user.save()
            return render(
                request,
                "app/success.html",
                {"message": "password reset successful"},
                status=200,
            )

        except DjangoUnicodeDecodeError as identifier:
            return render(
                request,
                "app/failure.html",
                {"message": "invalid token, request new one"},
                status=401,
            )


class ChangePasswordView(APIView):
    permission_classes = [CustomerAccessPermission]

    def put(self, request):
        user = request.user
        data = request.data
        if data["password"] != data["password2"]:
            return Response(
                {"message": "Password fields didn't match."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.check_password(data["old_password"]):
            return Response(
                {"message": "Old password is not correct."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(data["password"])
        user.save()
        return Response(
            {"message": "password change success"}, status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [CustomerAccessPermission]

    def delete(self, request):
        access_token = request.headers.get("Authorization").split(" ")[1]
        instance = Token.objects.get(access_token=access_token)
        instance.delete()

        return Response({"message": "success"}, status=status.HTTP_200_OK)


class QuestionsView(APIView):
    permission_classes = [CustomerAccessPermission]

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionView(APIView):
    permission_classes = [CustomerAccessPermission]

    def get(self, request, qstn_id):
        instance = Question.objects.get(id=qstn_id)
        serializer = QuestionSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, qstn_id):
        instance = Question.objects.get(id=qstn_id)
        serializer = QuestionSerializer(instance, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, qstn_id):
        instance = Question.objects.get(id=qstn_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaderBoardView(APIView):
    permission_classes = [CustomerAccessPermission]

    def get(self, request):
        leaderboard = LeaderBoard.objects.all()
        serializer = LeaderBoardSerializer(leaderboard, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = LeaderBoard(points=request.data["points"], user=request.user)
        data.save()
        return Response(status=status.HTTP_200_OK)

    def put(self, request):
        user_point = LeaderBoard.objects.get(user_id=request.user.id)
        user_point.points = request.data["points"] + user_point.points
        user_point.save()
        return Response(status=status.HTTP_200_OK)
