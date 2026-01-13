from django.contrib.auth import login
from drf_spectacular.utils import OpenApiResponse, extend_schema
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions

from apps.core.throttling import ActionBasedThrottle
from apps.users.serializers import UserSerializer

from .serializers import LoginSerializer


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    throttle_classes = KnoxLoginView.throttle_classes + [ActionBasedThrottle]
    throttle_method_scopes = {
        "post": "auth",
    }

    @extend_schema(
        summary="User Login",
        description="Authenticate user with username and password to get a Knox token.",
        request=LoginSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)
