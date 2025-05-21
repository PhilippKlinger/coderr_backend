from rest_framework.pagination import PageNumberPagination

class OfferPagination(PageNumberPagination):
    """
    Pagination class for offers, sets a default page size and allows page size query parameter.
    """
    page_size = 6
    page_size_query_param = "page_size"