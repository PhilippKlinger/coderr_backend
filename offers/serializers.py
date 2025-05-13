from rest_framework import serializers
from .models import Offer, OfferDetail
from rest_framework.reverse import reverse


# 🔹 Für GET /api/offers/ — nur Links zu Details
class OfferDetailReferenceSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        return reverse("offerdetail-retrieve", args=[obj.id], request=request)


# 🔹 Für GET /api/offers/ — Listenansicht
class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailReferenceSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        return min([d.price for d in obj.details.all()])

    def get_min_delivery_time(self, obj):
        return min([d.delivery_time_in_days for d in obj.details.all()])

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "first_name": obj.user.profile.first_name,
            "last_name": obj.user.profile.last_name,
        }


# 🔹 Für GET /api/offers/{id}/ — vollständige Details
class OfferDetailFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferDetailViewSerializer(serializers.ModelSerializer):
    details = OfferDetailFullSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]

    def get_min_price(self, obj):
        return min([d.price for d in obj.details.all()])

    def get_min_delivery_time(self, obj):
        return min([d.delivery_time_in_days for d in obj.details.all()])


# 🔹 Für POST/PATCH — Eingabedetails (kein Lesen)
class OfferDetailInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]

class OfferDetailSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


# 🔹 Für POST / PATCH (nested write)
class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailInputSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]
        read_only_fields = ["user", "min_price", "min_delivery_time", "user_details"]

    def get_min_price(self, obj):
        return min([detail.price for detail in obj.details.all()])

    def get_min_delivery_time(self, obj):
        return min([detail.delivery_time_in_days for detail in obj.details.all()])

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "first_name": obj.user.profile.first_name,
            "last_name": obj.user.profile.last_name,
        }

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data:
            instance.details.all().delete()
            for detail in details_data:
                OfferDetail.objects.create(offer=instance, **detail)

        return instance
