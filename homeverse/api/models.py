from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# =================================================================
# *** Authentication ***


# =================================================================
# *** Project ***
class Category(models.Model):
    CATEGORY_CHOICES = [
        ("traditional", "Traditional"),
        ("lux", "Lux"),
        ("super_lux", "Super Lux"),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Project(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField(max_length=20000)
    amount = models.DecimalField(decimal_places=1, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    project_image = models.ImageField(upload_to="projects/", null=True, blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="projects"
    )  # ربط المشروع بالتصنيف

    def __str__(self):
        return self.title


# Review
class Review(models.Model):
    rating = models.IntegerField()
    comment = models.TextField(max_length=1000)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"


class Request(models.Model):
    service_details = models.TextField()
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # الطلب مرتبط بمشروع
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
    )
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2)
