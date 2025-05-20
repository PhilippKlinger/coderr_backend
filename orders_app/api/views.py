from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from offers_app.models import OfferDetail

from orders_app.models import Order
from .permissions import IsCustomerUser, IsOrderOwnerOrReadOnly
from .serializers import OrderOutputSerializer, OrderSerializer, OrderCreateSerializer

User = get_user_model()


class OrderListCreateView(ListCreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsCustomerUser]
    search_fields = ["title"]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderOutputSerializer

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


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        if not User.objects.filter(id=business_user_id).exists():
            return Response(
                {"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND
            )

        count = Order.objects.filter(
            business_user__id=business_user_id, status="in_progress"
        ).count()
        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        if not User.objects.filter(id=business_user_id).exists():
            return Response(
                {"error": "Business user not found."}, status=status.HTTP_404_NOT_FOUND
            )

        count = Order.objects.filter(
            business_user__id=business_user_id, status="completed"
        ).count()
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
