from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from offers_app.models import OfferDetail
from orders_app.models import Order
from .permissions import IsCustomerUser, IsOrderOwnerOrReadOnly
from .serializers import OrderOutputSerializer, OrderSerializer, OrderCreateSerializer

User = get_user_model()

class OrderListCreateView(ListCreateAPIView):
    """
    API view to list all orders related to the current user or create a new order as a customer.
    """
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
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderOutputSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single order instance.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrReadOnly]
    lookup_field = "id"


class OrderCountView(APIView):
    """
    API view to retrieve the count of in-progress orders for a specific business user.
    """
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
    """
    API view to retrieve the count of completed orders for a specific business user.
    """
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
