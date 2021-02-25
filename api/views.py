from django.contrib.auth import authenticate, logout
import requests
from django.core.mail import send_mail
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.signals import reset_password_token_created
from oauth2_provider.admin import AccessToken
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailAddress
from django.urls import reverse
from rest_framework.views import APIView

from api.serializers import UserProfileSerializer, ChangePasswordSerializer
from accounts.models import UserProfile


@csrf_exempt
@api_view(['POST'])
def user_profile(request):
    serializer = UserProfileSerializer(request.user, many=False)

    email_address = EmailAddress.objects.get(email=request.user.email)
    if email_address.verified:
        return Response({'verified': True, 'profile': serializer.data})
    return Response({'verified': False, 'profile': serializer.data})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(email=request.data['email'], password=request.data['password'])
    if user:
        response = requests.post(
            'http://0.0.0.0:8000/o/token/',
            data={
                'grant_type': request.META.get('HTTP_GRANT_TYPE'),
                'username': request.data['email'],
                'password': request.data['password'],
                'client_id': request.META.get('HTTP_CLIENT_ID'),
                'client_secret': request.META.get('HTTP_CLIENT_SECRET'),
            }
        )
        return Response(response.json())
    else:
        return Response({'message': 'wrong information'})


@csrf_exempt
@api_view(['POST'])
@permission_classes({AllowAny})
def refresh_token(request):
    response = requests.post(
        'http://0.0.0.0:8000/o/token/',
        data={
            'grant_type': request.META.get('HTTP_GRANT_TYPE_REFRESH'),
            'refresh_token': request.data['refresh_token'],
            'client_id': request.META.get('HTTP_CLIENT_ID'),
            'client_secret': request.META.get('HTTP_CLIENT_SECRET'),
        }
    )
    return Response(response.json())


@csrf_exempt
@api_view(['POST'])
def revoke_token(request):
    token = AccessToken.objects.filter(user=request.user)
    response = requests.post(
        'http://0.0.0.0:8000/o/revoke_token/',
        data={
            'token': token,
            'client_id': request.META.get('HTTP_CLIENT_ID'),
            'client_secret': request.META.get('HTTP_CLIENT_SECRET'),
        },
    )
    if response.status_code == requests.codes.ok:
        return Response({'message': 'success'}, response.status_code)
    return Response({'error': 'fail'}, response.status_code)


@api_view(['POST'])
def change_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        # Check old password
        if not user.check_password(serializer.data.get("old_password")):
            return Response({"error": "Wrong old password"}, status=status.HTTP_400_BAD_REQUEST)
        # set_password also hashes the password that the user will get
        user.set_password(serializer.data.get("new_password"))
        user.save()
        response = {
            'message': 'Password updated successfully',
        }
        return Response(response)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    reset_token_user = ResetPasswordToken.objects.get(user_id=reset_password_token.user_id)
    title = "Password Reset for {title}.format(title=Forget password)"
    body = "This is your OTP: {token}".format(token=reset_token_user.key)

    send_mail(title, body, "admin@gmail.com", [reset_password_token.user.email])


@csrf_exempt
@api_view(['POST'])
def email_confirmation(request):
    email_address = EmailAddress.objects.get(email=request.user.email)

    if email_address.verified:
        return Response({'message': 'Email already verified'})

    send_email_confirmation(request, request.user)
    return Response({'message': 'Email confirmation resent'})


class UpdateEmail(APIView):

    def patch(self, request, format=None):
        user = request.user
        EmailAddress.objects.get(user=user.id).delete()

        user.email = request.data.get("email")
        user.save()
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

        send_email_confirmation(request, request.user)
        return Response({'message': 'Email confirmation sent'})


class ProfileUpdate(APIView):

    def patch(self, request, format=None):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
def email_verified_check(request):
    email_address = EmailAddress.objects.get(email=request.user.email)

    if email_address.verified:
        return Response({'email_verified': True})
    return Response({'email_verified': False})