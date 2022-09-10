from django.core.mail import EmailMessage
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed


from .models import Token


def check_whether_logged_out(access_token):
    token = None
    token = Token.objects.filter(access_token=access_token)
    if not token:
        return False
    return True


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["subject"], body=data["body"], to=[data["to"]]
        )
        email.send()


class CustomerAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        access_token = request.headers.get("Authorization").split(" ")[1]

        return bool(
            check_whether_logged_out(access_token)
            and request.user
            and request.user.is_authenticated
        )
