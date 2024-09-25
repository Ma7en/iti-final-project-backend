from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import *

urlpatterns = [
    path("project/", ProjectListCreate.as_view(), name="project-list"),
    path("project/delete/<int:pk>", ProjectDelete.as_view(), name="project-delete"),
    # user
    path("user/me/", UserDetailView.as_view(), name="user-detail"),
    # path("users/create/", create_user, name="get_user"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
