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
    file = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)
    location = models.CharField(max_length=50, blank=True, null=True, default="München")
    tel = models.CharField(max_length=20, blank=True, null=True, default="0152435465")
    description = models.CharField(max_length=150, blank=True, null=True, default="Deine Beschreibung")
    working_hours = models.CharField(max_length=20, blank=True, null=True, default="9-17")

    def __str__(self):
        return f"{self.user.username} - {self.type}"

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["-created_at"]
