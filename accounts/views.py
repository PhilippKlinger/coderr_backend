from django import views
from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Profile
from .serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)
from .permissions import IsProfileOwnerOrReadOnly
from rest_framework import views, status, generics
from rest_framework.authtoken.models import Token


class RegisterUserView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "token": token.key,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "user_id": user.pk,
                    "username": user.username,
                    "email": user.email,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]

    def get(self, request, pk):
        profile = get_object_or_404(Profile, user__pk=pk)
        self.check_object_permissions(request, profile)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk):
        profile = get_object_or_404(Profile, user__pk=pk)
        self.check_object_permissions(request, profile)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(type="business")


class CustomerProfileView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(type="customer")
