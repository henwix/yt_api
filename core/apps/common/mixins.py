from rest_framework import generics
from rest_framework.response import Response


class PaginationMixin(generics.GenericAPIView):
    def mixin_pagination(self, qs):
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response

    def mixin_filter_and_pagination(self, queryset):
        filtered_qs = self.filter_queryset(queryset)
        paginated_response = self.mixin_pagination(filtered_qs)
        if paginated_response:
            return paginated_response
        return Response(self.get_serializer(filtered_qs, many=True))
