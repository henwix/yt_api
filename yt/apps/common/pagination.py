from rest_framework.pagination import CursorPagination, PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomCursorPagination(CursorPagination):
    page_size = 10
    cursor_query_param = 'c'
    page_size_query_param = 'page_size'
    ordering = '-created_at'
    max_page_size = 50
