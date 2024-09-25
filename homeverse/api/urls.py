from django.urls import path
from .views import *

urlpatterns = [
    path("project/", ProjectListCreate.as_view(), name="project-list"),
    path("project/delete/<int:pk>", ProjectDelete.as_view(), name="project-delete"),
    # path("users/create/", create_user, name="get_user"),
]
