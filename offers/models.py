from django.db import models
from django.conf import settings


class Offer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offers"
    )
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="offer_images/", null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Offer"
        verbose_name_plural = "Offers"


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = (
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    )

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=100)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"

    class Meta:
        ordering = ["price"]
        verbose_name = "Offer Detail"
        verbose_name_plural = "Offer Details"
