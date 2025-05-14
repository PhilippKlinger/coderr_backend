from django.urls import path
from .views import OrderListCreateView, OrderRetrieveUpdateDestroyView

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:id>/", OrderRetrieveUpdateDestroyView.as_view(), name="order-detail"),
]
