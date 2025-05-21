from rest_framework import serializers
from django.contrib.auth import get_user_model

from accounts_app.models import Profile
from offers_app.models import OfferDetail
from orders_app.models import Order

User = get_user_model()

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for order objects. Used for retrieving, updating and deleting orders.
    """
    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "customer_user",
            "business_user",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new order from an offer detail.
    """
    offer_detail_id = serializers.IntegerField(write_only=True)

    def validate_offer_detail_id(self, value):
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "OfferDetail with this ID does not exist."
            )
        return value

    def create(self, validated_data):
        offer_detail = OfferDetail.objects.get(id=validated_data["offer_detail_id"])
        customer_user = self.context["request"].user
        business_user = offer_detail.offer.user

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )
        return order


class OrderOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for outputting order data, with user IDs for customer and business user.
    """
    customer_user = serializers.IntegerField(source="customer_user.id", read_only=True)
    business_user = serializers.IntegerField(source="business_user.id", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]