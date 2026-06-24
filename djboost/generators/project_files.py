import os


def create_directories():
    """Create standard Django project directories."""
    os.makedirs("apps", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("media", exist_ok=True)


def create_utils_file(name: str):
    """Global DRF exception handler — always returns clean JSON."""
    content = '''from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.
    Always returns: {"success": false, "message": "first error only"}
    """
    response = exception_handler(exc, context)

    if response is None:
        return response

    data = response.data

    if isinstance(data, dict) and "detail" in data:
        message = data["detail"]
    elif isinstance(data, dict):
        first_error = list(data.values())[0]
        message = first_error[0] if isinstance(first_error, list) else first_error
    elif isinstance(data, list):
        message = data[0]
    else:
        message = "Something went wrong."

    message = str(message)
    if "JSON parse error" in message:
        message = "Invalid JSON format in request body."

    response.data = {"success": False, "message": message}
    return response
'''
    with open(f"{name}/utils.py", "w", encoding="utf-8") as f:
        f.write(content)


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


# ── Example: send email async ─────────────────────────────────────────────────
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
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def root_view(request):
    return JsonResponse({"message": "API Server Running", "status": "ok"})


urlpatterns = [
    path('', root_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
    with open(f"{name}/urls.py", "w", encoding="utf-8") as f:
        f.write(content)
