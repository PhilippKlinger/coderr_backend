from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter

from reviews_app.models import Review
from .permissions import IsReviewerOrReadOnly
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewFilter(FilterSet):
    """
    Filter for reviews by business user or reviewer.
    """
    business_user_id = NumberFilter(field_name="business_user__id")
    reviewer_id = NumberFilter(field_name="reviewer__id")
    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]


class ReviewListCreateView(ListCreateAPIView):
    """
    API view to list all reviews or create a new review as a customer.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["updated_at", "rating"]

    def get_queryset(self):
        return Review.objects.all().order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a review.
    Only the original reviewer can update or delete.
    """
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, IsReviewerOrReadOnly]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ReviewUpdateSerializer
        return ReviewSerializer