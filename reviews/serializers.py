from rest_framework import serializers
from .models import Review

from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
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

        # Prüfen, ob der Nutzer ein Kunde ist
        if reviewer.profile.type != "customer":
            raise serializers.ValidationError("Nur Kunden dürfen Bewertungen abgeben.")

        # Prüfen, ob der Kunde bereits eine Bewertung abgegeben hat
        if Review.objects.filter(
            reviewer=reviewer, business_user=business_user
        ).exists():
            raise serializers.ValidationError(
                "Du hast bereits eine Bewertung abgegeben."
            )

        return data


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "description"]
