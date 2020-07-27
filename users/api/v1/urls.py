from django.urls import path
from .views import sign_up, ProfilePic
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("profile-pic", ProfilePic.as_view()),
    path("sign-up", sign_up),
    path("login", obtain_auth_token),
]