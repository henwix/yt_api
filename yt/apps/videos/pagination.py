from rest_framework.pagination import CursorPagination


class HistoryCursorPagination(CursorPagination):
    page_size = 10
    max_page_size = 20
    page_size_query_param = 'page_size'
    cursor_query_param = 'c'
    ordering = '-watched_at'
