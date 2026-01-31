"""
Pagination classes for ApeX Barbershop API.

Provides standardized pagination for all list endpoints.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class with customizable page size.
    
    Provides consistent pagination structure across all endpoints.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return a paginated response with metadata."""
        return Response(
            {
                "success": True,
                "data": data,
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "current_page": self.page.number,
                    "total_pages": self.page.paginator.num_pages,
                    "page_size": self.get_page_size(self.request),
                },
            }
        )


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class for large result sets.
    
    Use this for endpoints that typically return many results.
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_paginated_response(self, data):
        """Return a paginated response with metadata."""
        return Response(
            {
                "success": True,
                "data": data,
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "current_page": self.page.number,
                    "total_pages": self.page.paginator.num_pages,
                    "page_size": self.get_page_size(self.request),
                },
            }
        )


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination class for small result sets.
    
    Use this for endpoints that typically return few results.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        """Return a paginated response with metadata."""
        return Response(
            {
                "success": True,
                "data": data,
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "current_page": self.page.number,
                    "total_pages": self.page.paginator.num_pages,
                    "page_size": self.get_page_size(self.request),
                },
            }
        )
