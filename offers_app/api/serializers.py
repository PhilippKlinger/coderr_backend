from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
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
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
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
    id = serializers.IntegerField(required=False)

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
        prices = [d.price for d in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        times = [d.delivery_time_in_days for d in obj.details.all()]
        return min(times) if times else None

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
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

        if details_data is not None:
            # Update existing, add new, delete removed
            existing_details = {d.id: d for d in instance.details.all()}
            passed_ids = []
            for detail_data in details_data:
                detail_id = detail_data.get("id", None)
                if detail_id and detail_id in existing_details:
                    # Update existing detail
                    detail = existing_details[detail_id]
                    for key, value in detail_data.items():
                        if key != "id":
                            setattr(detail, key, value)
                    detail.save()
                    passed_ids.append(detail_id)
                else:
                    # Create new detail
                    OfferDetail.objects.create(
                        offer=instance,
                        **{k: v for k, v in detail_data.items() if k != "id"}
                    )
            # Delete details not included in PATCH
            for old_id, old_detail in existing_details.items():
                if old_id not in passed_ids:
                    old_detail.delete()
        return instance
