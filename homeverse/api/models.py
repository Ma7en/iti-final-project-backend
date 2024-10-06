from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.core.validators import RegexValidator

from shortuuid.django_fields import ShortUUIDField
import shortuuid


class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # email_username, mobile = self.email.split("@")
        email_username, _ = self.email.split("@")
        if self.full_name == "" or self.full_name == None:
            self.full_name = email_username
        if self.username == "" or self.username == None:
            self.username = email_username

        super(User, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(
        upload_to="user", default="user/default-user.png", null=True, blank=True
    )
    full_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone = models.CharField(
        max_length=12,
        validators=[
            RegexValidator(
                regex="^01[0|1|2|5][0-9]{8}$",
                message="Phone must be start 010, 011, 012, 015 and all number contains 11 digits",
            )
        ],
        blank=True,
    )
    about = models.TextField(null=True, blank=True)
    author = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.full_name:
            return str(self.full_name)
        else:
            return str(self.user.full_name)

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.full_name
        super(Profile, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe(
            '<img src="/media/user/%s" width="50" height="50" object-fit:"cover" style="border-radius: 30px; object-fit: cover;" />'
            % (self.image)
        )


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


# =================================================================
# *** Category ***
class Category(models.Model):
    title = models.CharField(max_length=300)
    details = models.CharField(max_length=30000, null=True, blank=True)
    image = models.FileField(upload_to="category", null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Category"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def post_count(self):
        return Post.objects.filter(category=self).count()


# =================================================================
# *** project ***
class Post(models.Model):
    STATUS = (
        ("Active", "Active"),
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="package", null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    status = models.CharField(max_length=100, choices=STATUS, default="Active")
    view = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="likes_user")
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Post"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + shortuuid.uuid()[:2]
        super(Post, self).save(*args, **kwargs)

    def comments(self):
        return Comment.objects.filter(post=self).order_by("-id")


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    description = models.TextField()
    email = models.CharField(max_length=100)
    comment = models.TextField()
    reply = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title} - {self.title}"

    class Meta:
        verbose_name_plural = "Comment"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title} - {self.user.username}"

    class Meta:
        verbose_name_plural = "Bookmark"


class Notification(models.Model):
    NOTI_TYPE = (("Like", "Like"), ("Comment", "Comment"), ("Bookmark", "Bookmark"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, choices=NOTI_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notification"

    def __str__(self):
        if self.post:
            return f"{self.type} - {self.post.title}"
        else:
            return "Notification"


# =================================================================
# *** Our work ***
class OurWork(models.Model):
    STATUS = (
        ("Active", "Active"),
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True
    )

    title = models.CharField(max_length=1000)
    description = models.TextField(null=True, blank=True)

    thumbnail = models.FileField(upload_to="ourwork", null=True, blank=True)
    image1 = models.FileField(upload_to="ourwork", null=True, blank=True)
    image2 = models.FileField(upload_to="ourwork", null=True, blank=True)
    image3 = models.FileField(upload_to="ourwork", null=True, blank=True)
    image4 = models.FileField(upload_to="ourwork", null=True, blank=True)

    # price_per_unit = models.DecimalField(max_digits=15, decimal_places=2)
    tags = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS, default="Active")
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "OurWork"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + shortuuid.uuid()[:2]
        super(OurWork, self).save(*args, **kwargs)


# =================================================================
# *** Register Order ***
""""
Sure! Here's the translation:

**Type of Residential Unit:**
- Apartment
- Full House
- Villa
- Roof
- Administrative
- Commercial Shop

**Required Works:**
- Execution only
- Execution and Design
- Supervision

**Skills:**
- Quick execution
- Material provision
- Innovative designs

**Condition of the Unit:**
- Unfinished
- Semi-finished
- 3/4 finished


"""


class RegisterOrder(models.Model):
    TYPE_UNIT = (
        ("Apartment", "Apartment"),
        ("FullHouse", "Full House"),
        ("Villa", "Villa"),
        ("Roof", "Roof"),
        ("Administrative", "Administrative"),
        ("CommercialShop", "Commercial Shop"),
    )
    REQUIRED_WORKS = (
        ("Executiononly", "Execution only"),
        ("ExecutionandDesign", "Execution and Design"),
        ("Supervision", "Supervision"),
    )
    SKILLS = (
        ("Quickexecution", "Quick execution"),
        ("Materialprovision", "Material provision"),
        ("Innovativedesigns", "Innovative designs"),
    )
    CONDITION_OF_THE_UNIT = (
        ("Unfinished", "Unfinished"),
        ("Semi-finished", "Semi-finished"),
        ("3/4finished", "3/4 finished"),
    )
    STATUS = (
        ("Active", "Active"),
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True
    )

    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(
        max_length=12,
        validators=[
            RegexValidator(
                regex="^01[0|1|2|5][0-9]{8}$",
                message="Phone must be start 010, 011, 012, 015 and all number contains 11 digits",
            )
        ],
        blank=True,
    )

    governorate = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    area = models.CharField(max_length=200)

    typeunit = models.CharField(max_length=300, choices=TYPE_UNIT, default="Apartment")
    requiredworks = models.CharField(
        max_length=300, choices=REQUIRED_WORKS, default="Executiononly"
    )
    skills = models.CharField(max_length=300, choices=SKILLS, default="Quickexecution")
    conditionoftheunit = models.CharField(
        max_length=300, choices=CONDITION_OF_THE_UNIT, default="Unfinished"
    )

    space = models.IntegerField(default=0)
    numberroom = models.IntegerField(default=0)
    numberbathroom = models.IntegerField(default=0)

    description = models.TextField(null=True, blank=True)

    # title = models.CharField(max_length=100)
    # image = models.FileField(upload_to="image", null=True, blank=True)
    # price_per_unit = models.DecimalField(max_digits=15, decimal_places=2)
    # tags = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS, default="Active")
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name_plural = "RegisterOrder"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = (
                slugify(self.full_name)
                + slugify(self.phone)
                + "-"
                + shortuuid.uuid()[:2]
            )
        super(RegisterOrder, self).save(*args, **kwargs)
