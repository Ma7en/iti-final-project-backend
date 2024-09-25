from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    amount = models.DecimalField(decimal_places=1, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    project_image = models.ImageField(upload_to="projects/", null=True, blank=True)

    def __str__(self):
        return self.title
