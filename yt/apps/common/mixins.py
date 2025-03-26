from rest_framework import generics


class PaginationMixin(generics.GenericAPIView):
    def mixin_pagination(self, qs):
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response
