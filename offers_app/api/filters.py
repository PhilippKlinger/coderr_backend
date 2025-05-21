from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework.filters import OrderingFilter, SearchFilter
from offers_app.models import Offer

class OfferFilter(FilterSet):
    creator_id = NumberFilter(field_name="user__id")
    min_price = NumberFilter(field_name="details__price", lookup_expr="gte")
    max_delivery_time = NumberFilter(field_name="details__delivery_time_in_days", lookup_expr="lte")

    class Meta:
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]
        
    def filter_min_price(self, queryset, name, value):
        return queryset.filter(details__price__gte=value).distinct()

    def filter_max_delivery_time(self, queryset, name, value):
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()

class OfferFilterConf:
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]