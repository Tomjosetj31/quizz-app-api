from django.contrib import auth

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import Question, User, Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]

        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "tokens"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials, try again")
        if not user.is_verified:
            raise AuthenticationFailed("Please verify your email")
        if not user.is_active:
            raise AuthenticationFailed("Account disabled, contact admin")
        refresh_token, access_token = user.tokens()
        token = Token(access_token=access_token, refresh_token=refresh_token, user=user)
        token.save()
        return {
            "email": email,
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        }


class UpdateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "accepted_terms_at",
            "is_verified",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=1000)
    answer = serializers.CharField(max_length=500)
    image_path = serializers.CharField(max_length=250)

    class Meta:
        model = Question
        fields = [
            "id",
            "question",
            "answer",
            "image_path",
            "created_at",
            "updated_at",
        ]

    def getAll():
        return Question.objects.all()

    def getQuestion(qstn_id):
        question = Question.objects.filter(id=qstn_id)
        return question
