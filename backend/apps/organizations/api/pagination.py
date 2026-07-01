from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination used across the organizations API.

    * Default page size: 20
    * Client may set ``page_size`` up to a maximum of 100.
    * Page number is supplied via the ``page`` query param.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"
