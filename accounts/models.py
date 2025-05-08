from datetime import date
from django.db import models
from django.conf import settings



class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField( max_length=15, blank=True, null=True)
    file = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    working_hours = models.CharField(max_length=20, blank=True, null=True)
    

    def __str__(self):
        return f"{self.user.username} - {self.type}"


