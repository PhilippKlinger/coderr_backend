from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter


from .models import Review
from .permissions import IsReviewerOrReadOnly
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewFilter(FilterSet):
    business_user_id = NumberFilter(field_name="business_user__id")
    reviewer_id = NumberFilter(field_name="reviewer__id")

    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]


class ReviewListCreateView(ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["updated_at", "rating"]

    def get_queryset(self):
        return Review.objects.all().order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, IsReviewerOrReadOnly]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ReviewUpdateSerializer
        return ReviewSerializer