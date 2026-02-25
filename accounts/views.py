import traceback
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


from .serializers import LoginSerializer, UserRegistrationSerializer, StaffRegistrationSerializer, SuperUserRegistrationSerializer
from utils.permissions import IsAdminUser
from utils.custom_response import ApiResponse

class UserLogin(APIView):

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return ApiResponse.error(
                    message="Invalid credentials.",
                    errors=serializer.errors,
                )

            return ApiResponse.success(
                data=serializer.validated_data,
                message="Login successful.",
            )
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))
        
class TokenRefreshAPIView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if not serializer.is_valid():
                return ApiResponse.error(
                    message="Invalid Token.",
                    errors=serializer.errors,
                )
            return ApiResponse.success(data=serializer.validated_data, message="Token refreshed successfully.")
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))
        


class CreateUserView(APIView):
    """
    Create a regular user is_active 1, is_super_user 0 is_staff 0.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return ApiResponse.error(
                        message="Invalid credentials.",
                        errors=serializer.errors,
                    )
            serializer.save()
            return ApiResponse.created(data=serializer.data, message="User created successfully")
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))


class CreateStaffView(APIView):
    """
    Create a staff user is_active 1, is_super_user 1.
    Only super user can create a staff user
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = StaffRegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return ApiResponse.error(
                            message="Invalid credentials.",
                            errors=serializer.errors,
                        )
            serializer.save()
            return ApiResponse.created(data=serializer.data, message="Staff user created")
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))


class CreateSuperUserView(APIView):
    """
    Create a superuser is_active 1, is_super_user 1 is_staff 1.
    Only existing superusers can create other superusers.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            if not request.user.is_superuser:
                return ApiResponse.forbidden()
            serializer = SuperUserRegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return ApiResponse.error(
                                message="Invalid credentials.",
                                errors=serializer.errors,
                            )
            serializer.save()
            return ApiResponse.created(data=serializer.data, message="Admin user created")
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))