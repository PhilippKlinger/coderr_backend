from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from offers.models import OfferDetail

from .models import Order
from .permissions import IsCustomerUser, IsOrderOwnerOrReadOnly
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderListCreateView(ListCreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsCustomerUser]
    search_fields = ["title"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get("offer_detail_id")
        if not offer_detail_id:
            return Response(
                {"error": "offer_detail_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            offer_detail = OfferDetail.objects.select_related("offer__user").get(
                pk=offer_detail_id
            )
        except OfferDetail.DoesNotExist:
            return Response(
                {"error": "OfferDetail not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrReadOnly]
    lookup_field = "id"
