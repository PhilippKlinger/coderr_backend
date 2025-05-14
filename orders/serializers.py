from rest_framework import serializers
from .models import Order
from offers.models import OfferDetail
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderSerializer(serializers.ModelSerializer):
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
            "status",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField(write_only=True)

    def validate_offer_detail_id(self, value):
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError("OfferDetail with this ID does not exist.")
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