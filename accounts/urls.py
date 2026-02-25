from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from django.urls import path
from .views import UserLogin, CreateUserView,CreateStaffView , CreateSuperUserView, TokenRefreshAPIView

urlpatterns = [

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token_refresh"),

    path("login/",UserLogin.as_view(),name="user login api"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("register/staff/", CreateStaffView.as_view(), name="register-staff"),
    path("register/superuser/", CreateSuperUserView.as_view(), name="register-superuser"),
]