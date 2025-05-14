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
    page_size = 10
    page_size_query_param = "page_size"


class OfferFilter(FilterSet):
    creator_id = NumberFilter(field_name="user", lookup_expr="exact")
    min_price = NumberFilter(field_name="details__price", lookup_expr="gte")
    max_delivery_time = NumberFilter(
        field_name="details__delivery_time_in_days", lookup_expr="lte"
    )

    class Meta:
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]


class OfferListCreateView(ListCreateAPIView):
    """
    GET  /api/offers/       -> list all offers, filterbar nach creator_id, min_price, max_delivery_time
    POST /api/offers/       -> create offer (Business-User), mindestens 3 details
    """
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OfferFilter
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
        return Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

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
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OfferDetailViewSerializer
        return OfferSerializer
    

class OfferDetailRetrieveView(RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSingleSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"