from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    Custom pagination with standard response format.
    
    Usage in views:
        paginator = CustomPagination()
        response = paginator.paginate_data(queryset, request, MySerializer)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data, additional_meta=None):
        meta = {
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
        }
        if additional_meta:
            meta.update(additional_meta)

        return Response({
            'success': True,
            'message': 'Data retrieved successfully.',
            'data': data,
            'meta': meta,
        })

    def paginate_data(
        self,
        queryset,
        request,
        serializer_class,
        many=False,
        context=None,
        message='Data retrieved successfully.',
        additional_meta=None,
        status_code=status.HTTP_200_OK,
    ):
        """
        One-liner pagination + serialization + response.
        
        Usage:
            paginator = CustomPagination()
            return paginator.paginate_data(
                queryset=queryset,
                request=request,
                serializer_class=UserSerializer,
            )
        """
        page = self.paginate_queryset(queryset, request)
        serializer = serializer_class(
            page if page is not None else queryset,
            many=many,
            context=context,
        )

        response = self.get_paginated_response(serializer.data, additional_meta)
        response.status_code = status_code
        response.data['message'] = message
        return response
