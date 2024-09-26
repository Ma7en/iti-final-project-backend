# =================================================================
# *** video ***
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics

# from .serializers import UserSerializer, ProjectSerializer
from .serializers import *
from .models import *

# =================================================================
# *** web ***
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.views import APIView

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets


# Create your views here.
# =================================================================
# *** Authentication ***
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


# =================================================================
# *** Project ***
# class CategoryViewSet(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [AllowAny]


# class ProjectViewSet(viewsets.ModelViewSet):
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         company = UserSerializer.objects.get(user=self.request.user)
#         serializer.save(author=self.request.user)
#         # serializer.save(company=company)

#     def get_queryset(self):
#         category = self.request.query_params.get("category", None)
#         if category:
#             return Project.objects.filter(category__name=category)
#         return super().get_queryset()


# class ReviewViewSet(viewsets.ModelViewSet):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#     permission_classes = [IsAuthenticated]


# class RequestViewSet(viewsets.ModelViewSet):
#     queryset = Request.objects.all()
#     serializer_class = RequestSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_company:
#             company = UserSerializer.objects.get(user=user)
#             return Request.objects.filter(project__company=company)
#         else:
#             return Request.objects.filter(customer=user)


# =================================================================
# *** video ***
class ProjectListCreate(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(author=user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class ProjectDelete(generics.DestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(author=user)
