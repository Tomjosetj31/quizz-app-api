import jwt
import datetime

from .utils import Util
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


from .serializers import UserSerializer, LoginSerializer
from .models import User


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

        email_body = "Hi Use link bbelow to verify your email \n" + absolute_url
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
