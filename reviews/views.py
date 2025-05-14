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
    filter_backends = [OrderingFilter]
    ordering_fields = ["updated_at", "rating"]

    def get_queryset(self):
        queryset = Review.objects.all().order_by("-updated_at")

        reviewer_id = self.request.query_params.get("reviewer_id")
        business_user_id = self.request.query_params.get("business_user_id")

        if reviewer_id and not reviewer_id.isdigit():
            import json
            try:
                parsed = json.loads(reviewer_id)
                reviewer_id = parsed.get("pk") or parsed.get("id")
            except Exception:
                reviewer_id = None

        if business_user_id and not business_user_id.isdigit():
            import json
            try:
                parsed = json.loads(business_user_id)
                business_user_id = parsed.get("pk") or parsed.get("id")
            except Exception:
                business_user_id = None

        if reviewer_id:
            queryset = queryset.filter(reviewer__id=reviewer_id)
        if business_user_id:
            queryset = queryset.filter(business_user__id=business_user_id)

        return queryset

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