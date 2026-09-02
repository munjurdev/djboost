import os
from pathlib import Path


def create_directories():
    """Create standard Django project directories."""
    os.makedirs("apps", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("media", exist_ok=True)
    os.makedirs("common", exist_ok=True)
    # Create __init__.py files
    Path("apps/__init__.py").touch()
    Path("common/__init__.py").touch()


def create_utils_file(name: str):
    """Create core/utils.py — imports exception handler from common.exceptions."""
    content = """from common.exceptions import custom_exception_handler


__all__ = ("custom_exception_handler",)
"""
    with open(f"{name}/utils.py", "w", encoding="utf-8") as f:
        f.write(content)


def create_common_files():
    """Create common/ package with responses.py, pagination.py, exceptions.py."""

    # common/responses.py
    responses_content = '''from rest_framework.response import Response
from rest_framework import status


def success_response(message="Success", data=None, status_code=status.HTTP_200_OK):
    """Standard success response format."""
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """Standard error response format."""
    return Response(
        {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
        },
        status=status_code,
    )
'''
    with open("common/responses.py", "w", encoding="utf-8") as f:
        f.write(responses_content)

    # common/pagination.py
    pagination_content = '''from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    Custom pagination with standard response format.

    Usage in views:
        from common.pagination import CustomPagination
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
        """One-liner pagination + serialization + response."""
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
'''
    with open("common/pagination.py", "w", encoding="utf-8") as f:
        f.write(pagination_content)

    # common/exceptions.py
    exceptions_content = '''from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.
    Always returns: {"success": false, "message": "...", "errors": null, "data": null}
    """
    response = exception_handler(exc, context)

    if response is None:
        from django.core.exceptions import ValidationError as DjangoValidationError
        from rest_framework.response import Response
        from rest_framework import status
        import traceback
        import logging

        logger = logging.getLogger(__name__)

        if isinstance(exc, DjangoValidationError):
            message = exc.messages[0] if hasattr(exc, 'messages') and exc.messages else str(exc)
            return Response({
                "success": False,
                "message": message,
                "errors": None,
                "data": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.error(f"Unhandled Exception: {exc}\\n{traceback.format_exc()}")

        return Response({
            "success": False,
            "message": "Internal Server Error. Please try again later.",
            "errors": None,
            "data": None,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = response.data
    message = "Something went wrong."
    errors = None

    if isinstance(data, dict) and "detail" in data:
        message = str(data["detail"])
    elif isinstance(data, dict):
        errors = data
        first_field = next(iter(data))
        first_error = data[first_field]
        if isinstance(first_error, (list, tuple)):
            first_error = first_error[0]
        message = str(first_error)
    elif isinstance(data, list):
        message = str(data[0])

    message = str(message)
    if "JSON parse error" in message:
        message = "Invalid JSON format in request body."
    elif message == "Authentication credentials were not provided.":
        message = "Authentication is required."
    elif message == "Not found.":
        message = "The requested resource was not found."

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
        "data": None,
    }
    return response
'''
    with open("common/exceptions.py", "w", encoding="utf-8") as f:
        f.write(exceptions_content)


def create_celery_file(name: str):
    """Celery app configuration."""
    content = f"""import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')

app = Celery('{name}')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {{self.request!r}}')
"""
    with open(f"{name}/celery.py", "w", encoding="utf-8") as f:
        f.write(content)


def create_tasks_file(name: str):
    """Sample Celery tasks file."""
    content = f"""from celery import shared_task


@shared_task
def sample_task():
    \"\"\"Sample Celery task - replace with your own logic.\"\"\"
    print("sample_task is running!")
    return "done"


# ── Example: send email async ─
# @shared_task
# def send_welcome_email(user_id):
#     from django.contrib.auth import get_user_model
#     User = get_user_model()
#     user = User.objects.get(id=user_id)
#     # send_mail(subject, message, from_email, [user.email])
#     return f"Email sent to {{user.email}}"
"""
    with open(f"{name}/tasks.py", "w", encoding="utf-8") as f:
        f.write(content)


def update_init_file(name: str):
    """Register Celery app in project __init__.py."""
    content = """from .celery import app as celery_app

__all__ = ('celery_app',)
"""
    with open(f"{name}/__init__.py", "w", encoding="utf-8") as f:
        f.write(content)


def update_urls_file(name: str):
    """Replace default urls.py with API-ready version."""
    content = """from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.http import JsonResponse


def root_view(request):
    return JsonResponse({"message": "API Server Running", "status": "ok"})


urlpatterns = [
    path("", root_view, name="home"),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
    with open(f"{name}/urls.py", "w", encoding="utf-8") as f:
        f.write(content)
