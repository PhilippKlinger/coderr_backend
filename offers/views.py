from warnings import filters
from django import views
from django.db.models import Min
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from .permissions import IsBusinessUser, IsOfferOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework import views, status
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Offer, OfferDetail
from .serializers import (
    OfferRetrieveSerializer,
    OfferSerializer,
    OfferDetailViewSerializer,
    OfferDetailSingleSerializer,
)


class OfferPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"


class OfferListCreateView(ListCreateAPIView):
    pagination_class = OfferPagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OfferRetrieveSerializer
        return OfferSerializer

    def get_queryset(self):
        queryset = (
            Offer.objects.all()
            .annotate(
                min_price=Min("details__price"),
                min_delivery_time=Min("details__delivery_time_in_days"),
            )
            .order_by("-created_at")
        )

        creator_id = self.request.query_params.get("creator_id")

        # Sonderfall: creator_id ist kein int (z. B. [object Object])
        if creator_id and not creator_id.isdigit():
            import json

            try:
                parsed = json.loads(creator_id)
                creator_id = parsed.get("pk") or parsed.get("id")
            except Exception:
                creator_id = None

        if creator_id:
            queryset = queryset.filter(user__id=creator_id)

        return queryset

    def post(self, request, *args, **kwargs):
        details = request.data.get("details", [])
        if len(details) < 3:
            return Response(
                {"error": "At least 3 offer details are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferDetailViewSerializer
    lookup_field = "id"

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsOfferOwnerOrReadOnly()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OfferDetailViewSerializer
        return OfferSerializer


class OfferDetailRetrieveView(RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSingleSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"
