from rest_framework import serializers
from reviews_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving reviews.
    Only customers can submit reviews, and only one review per business is allowed.
    """
    reviewer = serializers.ReadOnlyField(source="reviewer.id")

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate(self, data):
        request = self.context.get("request")
        reviewer = request.user
        business_user = data.get("business_user")

        if reviewer.profile.type != "customer":
            raise serializers.ValidationError("Nur Kunden dürfen Bewertungen abgeben.")

        if Review.objects.filter(
            reviewer=reviewer, business_user=business_user
        ).exists():
            raise serializers.ValidationError(
                "Du hast bereits eine Bewertung abgegeben."
            )

        return data


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating only the rating and description of a review.
    """
    class Meta:
        model = Review
        fields = ["rating", "description"]
