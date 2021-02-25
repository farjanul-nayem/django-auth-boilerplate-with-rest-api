from django.conf.urls import url
from django.urls import path, include
import api.views as apiView

urlpatterns = [
    path('login', apiView.login),
    path('refresh', apiView.refresh_token),
    path('logout', apiView.revoke_token),
    path('profile', apiView.user_profile),
    path('email-resend', apiView.email_confirmation),
    path('change-password', apiView.change_password),
    path('email-change', apiView.UpdateEmail.as_view()),
    path('profile-update', apiView.ProfileUpdate.as_view()),
    path('email-verified', apiView.email_verified_check),
    url(r'rest-auth/', include('rest_auth.urls')),
    url(r'signup', include('rest_auth.registration.urls')),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]