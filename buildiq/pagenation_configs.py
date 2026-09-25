from rest_framework.pagination import PageNumberPagination


class Pagination100PerPage(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class Pagination50PerPage(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class Pagination10PerPage(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class Pagination5PerPage(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
