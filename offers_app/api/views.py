from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Min

from .permissions import IsBusinessUser, IsOfferOwnerOrReadOnly
from offers_app.models import Offer, OfferDetail
from .serializers import (
    OfferRetrieveSerializer,
    OfferSerializer,
    OfferDetailViewSerializer,
    OfferDetailSingleSerializer,
)
from .pagination import OfferPagination
from .filters import OfferFilter, OfferFilterConf


class OfferListCreateView(ListCreateAPIView):
    """
    API view to list all offers or create a new offer.
    Provides pagination, search, ordering, and filtering by creator, price, and delivery time.
    """
    pagination_class = OfferPagination
    filterset_class = OfferFilter
    filter_backends = OfferFilterConf.filter_backends
    search_fields = OfferFilterConf.search_fields
    ordering_fields = OfferFilterConf.ordering_fields

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OfferRetrieveSerializer
        return OfferSerializer

    def get_queryset(self):
        queryset = Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        ).order_by("-created_at")
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
    """
    API view to retrieve, update, or delete a specific offer.
    GET requests are open to all, write operations require owner permissions.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferDetailViewSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OfferDetailViewSerializer
        return OfferSerializer


class OfferDetailRetrieveView(RetrieveAPIView):
    """
    API view to retrieve the full details of a single offer detail (package).
    Accessible by anyone.
    """

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSingleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
