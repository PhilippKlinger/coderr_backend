from django.urls import path
from .views import OfferListCreateView, OfferRetrieveUpdateDestroyView, OfferDetailRetrieveView

urlpatterns = [
  path('offers/', OfferListCreateView.as_view(), name='offers'),
  path("offers/<int:id>/", OfferRetrieveUpdateDestroyView.as_view(), name="offer-detail"),
  path("offerdetails/<int:id>/", OfferDetailRetrieveView.as_view(), name="offerdetail-retrieve"),


]