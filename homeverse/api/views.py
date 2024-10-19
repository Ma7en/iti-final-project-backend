from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Sum

# mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect


# Restframework
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

from django.contrib.auth.models import AnonymousUser

# Others
import json
import random

# Custom Imports
from api import serializer as api_serializer
from api import models as api_models

# from .models import *
# from .serializer import CategorySerializer


# =================================================================
# *** Admin ***
@api_view(["GET"])
def get_current_user(request):
    user = request.user
    return Response({"username": user.username, "is_superuser": user.is_superuser})


# =================================================================
# *** Authentication ***
# This code defines a DRF View class called MyTokenObtainPairView, which inherits from TokenObtainPairView.
class MyTokenObtainPairView(TokenObtainPairView):
    # Here, it specifies the serializer class to be used with this view.
    serializer_class = api_serializer.MyTokenObtainPairSerializer


# This code defines another DRF View class called RegisterView, which inherits from generics.CreateAPIView.
class RegisterView(generics.CreateAPIView):
    # It sets the queryset for this view to retrieve all User objects.
    queryset = api_models.User.objects.all()
    # It specifies that the view allows any user (no authentication required).
    permission_classes = (AllowAny,)
    # It sets the serializer class to be used with this view.
    serializer_class = api_serializer.RegisterSerializer


# This code defines another DRF View class called ProfileView, which inherits from generics.RetrieveAPIView and used to show user profile view.
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = api_serializer.ProfileSerializer

    def get_object(self):
        user_id = self.kwargs["user_id"]

        user = api_models.User.objects.get(id=user_id)
        profile = api_models.Profile.objects.get(user=user)
        return profile


def generate_numeric_otp(length=7):
    # Generate a random 7-digit OTP
    otp = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return otp


# =================================================================
# *** send mail ***
class PasswordEmailVerify(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs["email"]
        user = api_models.User.objects.get(email=email)

        if user:
            user.otp = generate_numeric_otp()
            uidb64 = user.pk

            # Generate a token and include it in the reset link sent via email
            refresh = RefreshToken.for_user(user)
            reset_token = str(refresh.access_token)

            # Store the reset_token in the user model for later verification
            user.reset_token = reset_token
            user.save()

            # *** edit here ***
            link = f"http://localhost:3000/changepassword?otp={user.otp}&uidb64={uidb64}&reset_token={reset_token}"
            # link = f"https://homeverse-1.vercel.app/changepassword?otp={user.otp}&uidb64={uidb64}&reset_token={reset_token}"

            merge_data = {
                "link": link,
                "username": user.username,
            }
            subject = f"Password Reset Request"
            text_body = render_to_string("email/password_reset.txt", merge_data)
            html_body = render_to_string("email/password_reset.html", merge_data)

            msg = EmailMultiAlternatives(
                subject=subject,
                from_email=settings.FROM_EMAIL,
                to=[user.email],
                body=text_body,
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
        return user


class PasswordChangeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        payload = request.data

        otp = payload["otp"]
        uidb64 = payload["uidb64"]
        password = payload["password"]

        user = api_models.User.objects.get(id=uidb64, otp=otp)
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()

            return Response(
                {"message": "Password Changed Successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "An Error Occured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =================================================================
# *** send mail ***
def send_confirmation_email(user):
    # إنشاء token فريد للمستخدم
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # بناء رابط التفعيل
    activation_link = reverse(
        "activate_account", kwargs={"uidb64": uid, "token": token}
    )

    # *** edit here ***
    activation_url = f"http://127.0.0.1:8000{activation_link}"
    # activation_url = f"https://m9ee9m4.pythonanywhere.com{activation_link}"

    subject = "Confirm your registration"
    message = f"Thank you for registering. Please confirm your email by clicking the link below:\n{activation_url}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


# =================================================================
# *** active account ***
class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        User = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # *** edit here ***
            # توجيه المستخدم إلى رابط React بعد التفعيل
            return HttpResponseRedirect("http://localhost:3000/login?activated=true")
            # return HttpResponseRedirect(
            #     "https://homeverse-1.vercel.app/login?activated=true"
            # )
        else:
            # *** edit here ***
            # إذا كان الرابط غير صالح، يمكن توجيهه إلى صفحة خطأ أو صفحة أخرى
            return HttpResponseRedirect("http://localhost:3000/error?activation=failed")
            # return HttpResponseRedirect(
            #     "https://homeverse-1.vercel.app/error?activation=failed"
            # )


# =================================================================
# *** Category3 ***


# *** Category List and Create ***
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]


# *** Category Retrieve, Update, and Delete ***
class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]


# =================================================================
# *** Category2 -> run ***
class CategoryListAPIView(generics.ListAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer

    def post(self, request, *args, **kwargs):
        if "image" not in request.FILES:
            return Response({"error": "Image file is required."}, status=400)
        return super().post(request, *args, **kwargs)


# Create a category
class CategoryCreateAPIView(generics.CreateAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer


# Update a category
class CategoryUpdateAPIView(generics.UpdateAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer

    def post(self, request, *args, **kwargs):
        if "image" not in request.FILES:
            return Response({"error": "Image file is required."}, status=400)
        return super().post(request, *args, **kwargs)


# views.py
class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer
    # lookup_field = "slug"


class CategoryDetailSlugAPIView(generics.RetrieveAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer
    lookup_field = "slug"


# Delete a category
class CategoryDeleteAPIView(generics.DestroyAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer


# =================================================================
# *** Category ***
class CategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Category.objects.all()


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CategoryRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = api_models.Category.objects.all()
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"


# =================================================================
# *** project ***
######################## Post APIs ########################
class PostCategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        category = api_models.Category.objects.get(slug=category_slug)
        return api_models.Post.objects.filter(category=category, status="Active")


class PostListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Post.objects.all()


class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs["slug"]
        post = api_models.Post.objects.get(slug=slug, status="Active")
        post.view += 1
        post.save()
        return post


class LikePostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "post_id": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        user_id = request.data["user_id"]
        post_id = request.data["post_id"]

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        # Check if post has already been liked by this user
        if user in post.likes.all():
            # If liked, unlike post
            post.likes.remove(user)
            return Response({"message": "Post Disliked"}, status=status.HTTP_200_OK)
        else:
            # If post hasn't been liked, like the post by adding user to set of poeple who have liked the post
            post.likes.add(user)

            # Create Notification for Author
            api_models.Notification.objects.create(
                user=post.user,
                post=post,
                type="Like",
            )
            return Response({"message": "Post Liked"}, status=status.HTTP_201_CREATED)


class PostCommentAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "post_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "title": openapi.Schema(type=openapi.TYPE_STRING),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "comment": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        # Get data from request.data (frontend)
        post_id = request.data["post_id"]
        name = request.data["name"]
        title = request.data["title"]
        description = request.data["description"]
        email = request.data["email"]
        comment = request.data["comment"]

        post = api_models.Post.objects.get(id=post_id)

        # Create Comment
        api_models.Comment.objects.create(
            post=post,
            name=name,
            title=title,
            description=description,
            email=email,
            comment=comment,
        )

        # Notification
        api_models.Notification.objects.create(
            user=post.user,
            post=post,
            type="Comment",
        )

        # Return response back to the frontend
        return Response({"message": "Component Sent"}, status=status.HTTP_201_CREATED)


class BookmarkPostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "post_id": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        user_id = request.data["user_id"]
        post_id = request.data["post_id"]

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        bookmark = api_models.Bookmark.objects.filter(post=post, user=user).first()
        if bookmark:
            # Remove post from bookmark
            bookmark.delete()
            return Response(
                {"message": "Post Un-Bookmarked"}, status=status.HTTP_200_OK
            )
        else:
            api_models.Bookmark.objects.create(user=user, post=post)

            # Notification
            api_models.Notification.objects.create(
                user=post.user,
                post=post,
                type="Bookmark",
            )
            return Response(
                {"message": "Post Bookmarked"}, status=status.HTTP_201_CREATED
            )


######################## Author Dashboard APIs ########################
class DashboardStats(generics.ListAPIView):
    serializer_class = api_serializer.AuthorStats
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = api_models.User.objects.get(id=user_id)

        views = api_models.Post.objects.filter(user=user).aggregate(view=Sum("view"))[
            "view"
        ]
        posts = api_models.Post.objects.filter(user=user).count()
        likes = api_models.Post.objects.filter(user=user).aggregate(
            total_likes=Sum("likes")
        )["total_likes"]
        bookmarks = api_models.Bookmark.objects.all().count()

        return [
            {
                "views": views,
                "posts": posts,
                "likes": likes,
                "bookmarks": bookmarks,
            }
        ]

    def list(self, request, *args, **kwargs):
        querset = self.get_queryset()
        serializer = self.get_serializer(querset, many=True)
        return Response(serializer.data)


class DashboardPostLists(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = api_models.User.objects.get(id=user_id)

        return api_models.Post.objects.filter(user=user).order_by("-id")


class DashboardCommentLists(generics.ListAPIView):
    serializer_class = api_serializer.CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Comment.objects.all()


class DashboardNotificationLists(generics.ListAPIView):
    serializer_class = api_serializer.NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = api_models.User.objects.get(id=user_id)

        return api_models.Notification.objects.filter(seen=False, user=user)


class DashboardMarkNotiSeenAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "noti_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        noti_id = request.data["noti_id"]
        noti = api_models.Notification.objects.get(id=noti_id)

        noti.seen = True
        noti.save()

        return Response({"message": "Noti Marked As Seen"}, status=status.HTTP_200_OK)


class DashboardPostCommentAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "comment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "reply": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        comment_id = request.data["comment_id"]
        reply = request.data["reply"]

        print("comment_id =======", comment_id)
        print("reply ===========", reply)

        comment = api_models.Comment.objects.get(id=comment_id)
        comment.reply = reply
        comment.save()

        return Response(
            {"message": "Comment Response Sent"}, status=status.HTTP_201_CREATED
        )


class DashboardPostCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(request.data)
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        price_per_unit = request.data.get("price_per_unit")
        image = request.data.get("image")
        description = request.data.get("description")
        tags = request.data.get("tags")
        category_id = request.data.get("category")
        post_status = request.data.get("post_status")

        print(user_id)
        print(title)
        print(price_per_unit)
        print(image)
        print(description)
        print(tags)
        print(category_id)
        print(post_status)

        user = api_models.User.objects.get(id=user_id)
        category = api_models.Category.objects.get(id=category_id)

        post = api_models.Post.objects.create(
            user=user,
            title=title,
            price_per_unit=price_per_unit,
            image=image,
            description=description,
            tags=tags,
            category=category,
            status=post_status,
        )

        return Response(
            {"message": "Post Created Successfully"}, status=status.HTTP_201_CREATED
        )


class DashboardPostEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        post_id = self.kwargs["post_id"]
        user = api_models.User.objects.get(id=user_id)
        return api_models.Post.objects.get(user=user, id=post_id)

    def update(self, request, *args, **kwargs):
        post_instance = self.get_object()

        title = request.data.get("title")
        price_per_unit = request.data.get("price_per_unit")
        image = request.data.get("image")
        description = request.data.get("description")
        tags = request.data.get("tags")
        category_id = request.data.get("category")
        post_status = request.data.get("post_status")

        print(title)
        print(price_per_unit)
        print(image)
        print(description)
        print(tags)
        print(category_id)
        print(post_status)

        category = api_models.Category.objects.get(id=category_id)

        post_instance.title = title
        if image != "undefined":
            post_instance.image = image
        post_instance.description = description
        post_instance.price_per_unit = price_per_unit
        post_instance.tags = tags
        post_instance.category = category
        post_instance.status = post_status
        post_instance.save()

        return Response(
            {"message": "Post Updated Successfully"}, status=status.HTTP_200_OK
        )


# Delete a category
class DashboardPostDeleteAPIView(generics.DestroyAPIView):
    queryset = api_models.Post.objects.all()
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]


# =================================================================
# *** Our Work ***


# create
class OurWorkCreateAPIView(generics.CreateAPIView):
    queryset = api_models.OurWork.objects.all()
    serializer_class = api_serializer.OurWorkSerializer

    def create(self, request, *args, **kwargs):
        try:
            post = api_models.OurWork.objects.create(
                user_id=request.data["user_id"],
                title=request.data["title"],
                description=request.data["description"],
                thumbnail=request.data["thumbnail"],
                image1=request.data["image1"],
                image2=request.data["image2"],
                image3=request.data["image3"],
                image4=request.data["image4"],
                tags=request.data["tags"],
                status=request.data["post_status"],
            )
            return Response(
                {"message": "Our Work created successfully."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# update
class OurWorkUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.OurWorkSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        ourwork_id = self.kwargs["ourwork_id"]
        user = api_models.User.objects.get(id=user_id)
        return api_models.OurWork.objects.get(user=user, id=ourwork_id)

    def update(self, request, *args, **kwargs):
        ourwork_instance = self.get_object()

        title = request.data.get("title")
        description = request.data.get("description")

        # price_per_unit = request.data.get("price_per_unit")
        thumbnail = request.data.get("thumbnail")

        image1 = request.data.get("image1")
        image2 = request.data.get("image2")
        image3 = request.data.get("image3")
        image4 = request.data.get("image4")

        tags = request.data.get("tags")
        post_status = request.data.get("post_status")

        #

        ourwork_instance.title = title
        ourwork_instance.description = description

        if thumbnail != "undefined":
            ourwork_instance.thumbnail = thumbnail

        if image1 != "undefined":
            ourwork_instance.image1 = image1
        if image2 != "undefined":
            ourwork_instance.image2 = image2
        if image3 != "undefined":
            ourwork_instance.image3 = image3
        if image4 != "undefined":
            ourwork_instance.image4 = image4

        # ourwork_instance.price_per_unit = price_per_unit
        ourwork_instance.tags = tags
        ourwork_instance.status = post_status
        ourwork_instance.save()

        return Response(
            {"message": "Our Work Updated Successfully"},
            status=status.HTTP_200_OK,
        )


# List
class OurWorkListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.OurWorkSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.OurWork.objects.all()


# Details
class OurWorkDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.OurWorkSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs["slug"]
        post = api_models.OurWork.objects.get(slug=slug)
        # post.view += 1
        post.save()
        return post


# Delete a our work
class OurWorkDeleteAPIView(generics.DestroyAPIView):
    queryset = api_models.OurWork.objects.all()
    serializer_class = api_serializer.OurWorkSerializer
    permission_classes = [AllowAny]


# =================================================================
# *** Register Order ***
"""
create 
author/dashboard/post-create/
update
author/dashboard/post-detail/${userId}/${param.id}/

list 
post/lists/
details
post/detail/${param.slug}/

detele 
author/dashboard/post-delete/${userId}/${id}/


"""


def get_queryset(self):
    user = self.request.user

    # Check if the user is authenticated
    if isinstance(user, AnonymousUser):
        return (
            api_models.RegisterOrder.objects.none()
        )  # Return an empty queryset for anonymous users
    else:
        return api_models.RegisterOrder.objects.filter(user=user)


# class DashboardRegisterOrderCreateAPIView(generics.CreateAPIView):
#     queryset = api_models.RegisterOrder.objects.all()
#     serializer_class = api_serializer.RegisterOrderSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         print(request.data)
#         user_id = request.data.get("user_id")

#         full_name = request.data.get("full_name")
#         phone = request.data.get("phone")

#         governorate = request.data.get("governorate")
#         city = request.data.get("city")
#         area = request.data.get("area")

#         typeunit = request.data.get("typeunit")
#         requiredworks = request.data.get("requiredworks")
#         skills = request.data.get("skills")
#         conditionoftheunit = request.data.get("conditionoftheunit")

#         space = request.data.get("space")
#         numberroom = request.data.get("numberroom")
#         numberbathroom = request.data.get("numberbathroom")

#         description = request.data.get("description")

#         # title = request.data.get("title")
#         # price_per_unit = request.data.get("price_per_unit")
#         # image = request.data.get("image")
#         # tags = request.data.get("tags")
#         post_status = request.data.get("post_status")

#         # print(user_id)
#         # print(title)
#         # print(price_per_unit)
#         # print(image)
#         # print(description)
#         # print(tags)
#         # print(post_status)

#         user = api_models.User.objects.get(id=user_id)

#         post = api_models.Post.objects.create(
#             user=user,
#             full_name=full_name,
#             phone=phone,
#             governorate=governorate,
#             city=city,
#             area=area,
#             typeunit=typeunit,
#             requiredworks=requiredworks,
#             skills=skills,
#             conditionoftheunit=conditionoftheunit,
#             space=space,
#             numberroom=numberroom,
#             numberbathroom=numberbathroom,
#             description=description,
#             # title=title,
#             # price_per_unit=price_per_unit,
#             # image=image,
#             # tags=tags,
#             status=post_status,
#         )

#         return Response(
#             {"message": "Register Order Created Successfully"},
#             status=status.HTTP_201_CREATED,
#         )


class DashboardRegisterOrderCreateAPIView(generics.CreateAPIView):
    queryset = api_models.RegisterOrder.objects.all()
    serializer_class = api_serializer.RegisterOrderSerializer

    def create(self, request, *args, **kwargs):
        try:
            post = api_models.RegisterOrder.objects.create(
                user_id=request.data["user_id"],
                full_name=request.data["full_name"],
                phone=request.data["phone"],
                governorate=request.data["governorate"],
                city=request.data["city"],
                area=request.data["area"],
                typeunit=request.data["typeunit"],
                requiredworks=request.data["requiredworks"],
                skills=request.data["skills"],
                conditionoftheunit=request.data["conditionoftheunit"],
                space=request.data["space"],
                numberroom=request.data["numberroom"],
                numberbathroom=request.data["numberbathroom"],
                description=request.data["description"],
                package=request.data["package"],
                status=request.data["post_status"],
            )
            return Response(
                {"message": "Order Created Successfully."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class DashboardRegisterOrderCreateAPIView(generics.CreateAPIView):
#     queryset = api_models.RegisterOrder.objects.all()
#     serializer_class = api_serializer.RegisterOrderSerializer
#     permission_classes = [AllowAny]


class DashboardRegisterOrderEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.RegisterOrderSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        registerorder_id = self.kwargs["registerorder_id"]
        user = api_models.User.objects.get(id=user_id)
        return api_models.RegisterOrder.objects.get(user=user, id=registerorder_id)

    def update(self, request, *args, **kwargs):
        registerorder_instance = self.get_object()

        full_name = request.data.get("full_name")
        phone = request.data.get("phone")

        governorate = request.data.get("governorate")
        city = request.data.get("city")
        area = request.data.get("area")

        typeunit = request.data.get("typeunit")
        requiredworks = request.data.get("requiredworks")
        skills = request.data.get("skills")
        conditionoftheunit = request.data.get("conditionoftheunit")

        space = request.data.get("space")
        numberroom = request.data.get("numberroom")
        numberbathroom = request.data.get("numberbathroom")

        description = request.data.get("description")

        title = request.data.get("title")
        price_per_unit = request.data.get("price_per_unit")
        image = request.data.get("image")
        tags = request.data.get("tags")
        post_status = request.data.get("post_status")

        # print(title)
        # print(price_per_unit)
        # print(image)
        # print(description)
        # print(tags)
        # print(category_id)
        # print(post_status)

        registerorder_instance.full_name = full_name
        registerorder_instance.phone = phone

        registerorder_instance.governorate = governorate
        registerorder_instance.city = city
        registerorder_instance.area = area

        registerorder_instance.typeunit = typeunit
        registerorder_instance.typeunit = typeunit
        registerorder_instance.skills = skills
        registerorder_instance.conditionoftheunit = conditionoftheunit

        registerorder_instance.space = space
        registerorder_instance.numberroom = numberroom
        registerorder_instance.numberbathroom = numberbathroom

        registerorder_instance.description = description
        registerorder_instance.title = title
        if image != "undefined":
            registerorder_instance.image = image
        registerorder_instance.price_per_unit = price_per_unit
        registerorder_instance.tags = tags
        registerorder_instance.status = post_status
        registerorder_instance.save()

        return Response(
            {"message": "Register Order Updated Successfully"},
            status=status.HTTP_200_OK,
        )


# handle admin
class RegisterOrderListAdminAPIView(generics.ListAPIView):
    serializer_class = api_serializer.RegisterOrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.RegisterOrder.objects.all()


class RegisterOrderListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.RegisterOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return api_models.RegisterOrder.objects.all()
        else:
            return api_models.RegisterOrder.objects.filter(user=user)


# handle admin
class RegisterOrderDetailAdminAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.RegisterOrderSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs["slug"]
        post = api_models.RegisterOrder.objects.get(slug=slug)
        # post.view += 1
        post.save()
        return post


class RegisterOrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.RegisterOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        slug = self.kwargs["slug"]
        try:
            post = api_models.RegisterOrder.objects.get(slug=slug)
            if user.is_superuser or post.user == user:
                return post
            else:
                raise PermissionDenied("You do not have permission to view this order.")
        except api_models.RegisterOrder.DoesNotExist:
            raise NotFound("Order not found.")


# handle
# class RegisterOrderDetailAPIView(generics.RetrieveAPIView):
#     serializer_class = api_serializer.RegisterOrderSerializer
#     permission_classes = [AllowAny]

#     def get_object(self):
#         slug = self.kwargs["slug"]
#         try:
#             post = api_models.RegisterOrder.objects.get(slug=slug)
#             post.view += 1
#             post.save()
#             return post
#         except api_models.RegisterOrder.DoesNotExist:
#             return None  # يمكن تحسين معالجة الأخطاء بإرجاع ردود مناسبة


# Delete a category
# class DashboardRegisterOrderDeleteAPIView(generics.DestroyAPIView):
#     queryset = api_models.RegisterOrder.objects.all()
#     serializer_class = api_serializer.PostSerializer
#     permission_classes = [AllowAny]


class DashboardRegisterOrderDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.RegisterOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return api_models.RegisterOrder.objects.all()
        else:
            return api_models.RegisterOrder.objects.filter(user=user)


{
    "title": "New post",
    "image": "",
    "description": "lorem",
    "tags": "tags, here",
    "category_id": 1,
    "post_status": "Active",
}
