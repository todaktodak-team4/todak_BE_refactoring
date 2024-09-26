from rest_framework.pagination import PageNumberPagination

class MemorialHallPagination(PageNumberPagination):
    page_size = 6  # 한 페이지에 나타낼 객체 수
    page_size_query_param = 'page_size'  # 클라이언트가 각 페이지의 크기를 재정의할 수 있도록 허용
    max_page_size = 100  # 최대 페이지 크기 제한
    
class MessagePagination(PageNumberPagination):
    page_size = 3  
    page_size_query_param = 'page_size'  
    max_page_size = 300