from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views


urlpatterns = [
    # Userauths API Endpoints
    path(
        "user/token/",
        api_views.MyTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("user/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/register/", api_views.RegisterView.as_view(), name="auth_register"),
    path(
        "user/profile/<user_id>/", api_views.ProfileView.as_view(), name="user_profile"
    ),
    path(
        "user/password-reset/<email>/",
        api_views.PasswordEmailVerify.as_view(),
        name="password_reset",
    ),
    path(
        "user/password-change/",
        api_views.PasswordChangeView.as_view(),
        name="password_reset",
    ),
    # category
    path(
        "category/list/", api_views.CategoryListAPIView.as_view(), name="category-list"
    ),
    path(
        "category/create/",
        api_views.CategoryCreateAPIView.as_view(),
        name="category-create",
    ),
    path(
        "category/update/<int:pk>/",
        api_views.CategoryUpdateAPIView.as_view(),
        name="category-update",
    ),
    path(
        "category/delete/<int:pk>/",
        api_views.CategoryDeleteAPIView.as_view(),
        name="category-delete",
    ),
    # category
    path(
        "categories/",
        api_views.CategoryListCreateAPIView.as_view(),
        name="category-list-create",
    ),
    path(
        "categories/<slug:slug>/",
        api_views.CategoryRetrieveUpdateAPIView.as_view(),
        name="category-detail-update",
    ),
    # Post Endpoints
    # path(
    #     "post/category/list/",
    #     api_views.CategoryListCreateAPIView.as_view(),
    #     name="category-list-create",
    # ),
    # path(
    #     "post/category/<slug:slug>/",
    #     api_views.CategoryRetrieveUpdateDestroyAPIView.as_view(),
    #     name="category-detail",
    # ),
    #
    path("post/category/list/", api_views.CategoryListAPIView.as_view()),
    path(
        "post/category/posts/<category_slug>/",
        api_views.PostCategoryListAPIView.as_view(),
    ),
    path("post/lists/", api_views.PostListAPIView.as_view()),
    path("post/detail/<slug>/", api_views.PostDetailAPIView.as_view()),
    path("post/like-post/", api_views.LikePostAPIView.as_view()),
    path("post/comment-post/", api_views.PostCommentAPIView.as_view()),
    path("post/bookmark-post/", api_views.BookmarkPostAPIView.as_view()),
    # Dashboard APIS
    path("author/dashboard/stats/<user_id>/", api_views.DashboardStats.as_view()),
    path(
        "author/dashboard/post-list/<user_id>/", api_views.DashboardPostLists.as_view()
    ),
    path("author/dashboard/comment-list/", api_views.DashboardCommentLists.as_view()),
    path(
        "author/dashboard/noti-list/<user_id>/",
        api_views.DashboardNotificationLists.as_view(),
    ),
    path(
        "author/dashboard/noti-mark-seen/",
        api_views.DashboardMarkNotiSeenAPIView.as_view(),
    ),
    path(
        "author/dashboard/reply-comment/",
        api_views.DashboardPostCommentAPIView.as_view(),
    ),
    path(
        "author/dashboard/post-create/", api_views.DashboardPostCreateAPIView.as_view()
    ),
    path(
        "author/dashboard/post-detail/<user_id>/<post_id>/",
        api_views.DashboardPostEditAPIView.as_view(),
    ),
]
