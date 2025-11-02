from django.db.models.query import QuerySet
from rest_framework import generics
from rest_framework.response import Response


class CustomViewMixin(generics.GenericAPIView):
    def _mixin_pagination(self, queryset: QuerySet) -> Response | None:
        """Retrieve queryset and returns paginated response if pagination
        enabled.

        Returns None if pagination disabled.

        """
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def mixin_filtration_and_pagination(self, queryset: QuerySet) -> Response:
        """
        Retrieve the queryset and return a Response.
        This method checks if pagination is enabled and returns the appropriate response:

        a paginated Response if pagination is active, or a regular serialized Response otherwise.
        """
        #  Filter queryset
        filtered_queryset: QuerySet = self.filter_queryset(queryset)

        #  Retrieve paginated response if pagination enabled
        paginated_response: Response | None = self._mixin_pagination(filtered_queryset)

        #  Return paginated response if it's not None
        if paginated_response is not None:
            return paginated_response

        #  Return Response based on 'filtered_queryset' without pagination
        return Response(self.get_serializer(filtered_queryset, many=True).data)

    def mixin_cache_and_response(self, cache_key: str, timeout: int, queryset: QuerySet) -> Response:
        """
        Note: This method depends on `cache_service`, which must be resolved via `punq.Container`
        in the main view method before calling this.

        Uses the 'mixin_filtration_and_pagination' method, caches the response, and returns it.
        """
        if not hasattr(self, 'cache_service'):
            raise AttributeError("Expected 'cache_service' to be injected before calling this method.")

        #  Retrieve the response after applying filtration and pagination
        response = self.mixin_filtration_and_pagination(queryset=queryset)

        #  Cache the serialized response data
        self.cache_service.set(cache_key, response.data, timeout)

        #  Return the response
        return response
