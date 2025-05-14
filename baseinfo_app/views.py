# baseinfo/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Avg, Count
from reviews.models import Review
from accounts.models import Profile
from offers.models import Offer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0
        business_profile_count = Profile.objects.filter(type="business").count()
        offer_count = Offer.objects.count()

        return Response({
            "review_count": review_count,
            "average_rating": round(average_rating, 1),
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        })
