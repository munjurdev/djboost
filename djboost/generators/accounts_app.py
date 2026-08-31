"""
Complete accounts app generator — creates a production-ready accounts module
with Custom User, OTP auth, social login, admin roles, and profile management.
"""

import os
import re
from pathlib import Path

from rich import print


def get_project_name():
    """Extract project name from manage.py."""
    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Are you in the project root?[/red]")
        return None

    content = Path("manage.py").read_text(encoding="utf-8")
    match = re.search(r"['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^.]+)\.settings['\"]", content)
    if match:
        return match.group(1)

    print("[red]Error: Could not determine project name from manage.py[/red]")
    return None


def create_accounts_directories():
    """Create accounts app directory structure."""
    dirs = [
        "apps/accounts",
        "apps/accounts/views",
        "apps/accounts/serializers",
        "apps/accounts/migrations",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        init_path = Path(d) / "__init__.py"
        if not init_path.exists():
            init_path.touch()


def create_accounts_models():
    """Create accounts/models.py with Custom User, EmailOTP, AdminSectionPermission."""
    content = '''import random
import string
import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Abstract base model with created_at and updated_at."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email address is required."))

        email = self.normalize_email(email).lower()
        extra_fields.setdefault("role", User.Role.USER)

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", User.Role.SUPER_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        ADMIN = "ADMIN", "Admin"
        USER = "USER", "User"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    full_name = models.CharField(max_length=255)

    email = models.EmailField(unique=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER, db_index=True)

    # Profile
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    bio = models.TextField(blank=True, null=True)

    website = models.URLField(blank=True, null=True)

    # User Settings
    push_notification = models.BooleanField(default=True)

    daily_reminder = models.BooleanField(default=False)

    reminder_time = models.TimeField(blank=True, null=True)

    # Social Login
    social_id = models.CharField(max_length=255, blank=True, null=True)

    social_provider = models.CharField(max_length=20, blank=True, null=True, choices=[("google", "Google"), ("facebook", "Facebook"), ("apple", "Apple")])

    # Account Status
    is_verified = models.BooleanField(default=False)

    is_blocked = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    # Security
    reset_secret_key = models.UUIDField(default=uuid.uuid4, editable=False)

    # Admin invitation validity
    invitation_expires_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(fields=["social_id", "social_provider"], condition=models.Q(social_id__isnull=False), name="unique_social_account"),
        ]

    def clean(self):
        if self.role == self.Role.SUPER_ADMIN and self.is_blocked:
            raise ValidationError(_("Super Admin cannot be blocked."))

    def __str__(self):
        return self.full_name

    @property
    def is_admin(self):
        return self.role in (self.Role.SUPER_ADMIN, self.Role.ADMIN)

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN


class AdminSectionPermission(TimeStampedModel):
    """
    Global section-level access settings for ALL Admin users.
    One entry per section — whatever is set here applies to every Admin.
    Super Admin manages these; Admins are bound by the global rules.
    """

    class Section(models.TextChoices):
        LEVELS_STORIES = "LEVELS_STORIES", "Levels & Stories"
        AUDIO = "AUDIO", "Audio Management"
        QUIZ = "QUIZ", "Quiz Management"
        USERS = "USERS", "Users"
        LEGAL = "LEGAL", "Legal (T&C / Privacy Policy)"
        OVERVIEW = "OVERVIEW", "Dashboard Overview"

    class Access(models.TextChoices):
        NONE = "NONE", "No Access"
        VIEW = "VIEW", "View"
        EDIT = "EDIT", "Edit"
        DELETE = "DELETE", "Delete"

    section = models.CharField(max_length=50, choices=Section.choices, unique=True, verbose_name="Section")

    access = models.CharField(max_length=10, choices=Access.choices, default=Access.NONE, verbose_name="Access Level")

    class Meta:
        db_table = "admin_section_permissions"
        verbose_name = "Admin Section Permission"
        verbose_name_plural = "Admin Section Permissions"

    def __str__(self):
        return f"{self.get_section_display()}: {self.get_access_display()}"


class EmailOTP(TimeStampedModel):
    class Purpose(models.TextChoices):
        SIGNUP = "SIGNUP", "Signup"
        RESET_PASSWORD = "RESET_PASSWORD", "Reset Password"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_otps")

    code = models.CharField(max_length=6)

    purpose = models.CharField(max_length=30, choices=Purpose.choices)

    is_used = models.BooleanField(default=False)

    attempt_count = models.PositiveSmallIntegerField(default=0)

    expires_at = models.DateTimeField()

    class Meta:
        db_table = "email_otps"
        ordering = ["-created_at"]

        indexes = [models.Index(fields=["user", "purpose"]), models.Index(fields=["expires_at"])]

    def __str__(self):
        return f"{self.user.email} - {self.purpose}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    @classmethod
    def generate_code(cls, length=6):
        return "".join(random.choices(string.digits, k=length))

    @classmethod
    def default_expiry(cls, minutes=5):
        return timezone.now() + timezone.timedelta(minutes=minutes)
'''
    path = Path("apps/accounts/models.py")
    path.write_text(content, encoding="utf-8")
    print("[green]✔ Created apps/accounts/models.py[/green]")


def create_accounts_permissions():
    """Create accounts/permissions.py with role-based access."""
    content = '''from rest_framework import permissions

from apps.accounts.models import AdminSectionPermission, User


class IsSuperAdmin(permissions.BasePermission):
    """Allow access only to users with SUPER_ADMIN role."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_blocked
            and request.user.role == User.Role.SUPER_ADMIN
        )


class IsAdmin(permissions.BasePermission):
    """Allow access only to users with ADMIN or SUPER_ADMIN role."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_blocked
            and request.user.role in (User.Role.SUPER_ADMIN, User.Role.ADMIN)
        )


class HasSectionAccess(permissions.BasePermission):
    """
    Check if the user has access to a specific admin section.

    Access Hierarchy (each level includes the previous):
        DELETE → Full access (all HTTP methods)
        EDIT   → Read + Create + Update (no DELETE allowed)
        VIEW   → Read-only (safe methods: GET, HEAD, OPTIONS)
        NONE   → No access

    Usage:
        class MyView(APIView):
            permission_classes = [HasSectionAccess]
            section = AdminSectionPermission.Section.LEVELS_STORIES
    """

    section = None

    def has_permission(self, request, view):
        user = request.user

        # Must be authenticated
        if not user or not user.is_authenticated:
            return False

        # Blocked accounts lose ALL admin access
        if user.is_blocked:
            return False

        # Super Admin has full access to everything
        if user.role == User.Role.SUPER_ADMIN:
            return True

        # Only Admin users can have section-level permissions
        if user.role != User.Role.ADMIN:
            return False

        # Get section from view or default
        section = getattr(view, "section", self.section)
        if not section:
            return False

        # Check the global section permission setting
        try:
            section_perm = AdminSectionPermission.objects.get(section=section)
        except AdminSectionPermission.DoesNotExist:
            return False

        access_level = section_perm.access

        # NONE → no access
        if access_level == AdminSectionPermission.Access.NONE:
            return False

        # VIEW → only safe methods allowed (GET, HEAD, OPTIONS)
        if access_level == AdminSectionPermission.Access.VIEW:
            return request.method in permissions.SAFE_METHODS

        # EDIT → safe methods + POST + PUT/PATCH, but DELETE is NOT allowed
        if access_level == AdminSectionPermission.Access.EDIT:
            if request.method == "DELETE":
                return False
            return True

        # DELETE → all HTTP methods allowed
        if access_level == AdminSectionPermission.Access.DELETE:
            return True

        return False


class IsOwner(permissions.BasePermission):
    """Allow access only to the owner of the object."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user
'''
    path = Path("apps/accounts/permissions.py")
    path.write_text(content, encoding="utf-8")
    print("[green]✔ Created apps/accounts/permissions.py[/green]")


def create_accounts_tasks():
    """Create accounts/tasks.py with Celery tasks."""
    content = '''"""
Celery background tasks for the accounts app.

Tasks are auto-discovered by Celery via autodiscover_tasks().
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_otp_email_task(user_id, otp_code, purpose):
    """
    Send an OTP verification code via email in the background.

    Uses Celery for reliable async execution with automatic retries.

    Args:
        user_id: UUID of the User instance.
        otp_code: The 6-digit OTP code.
        purpose: 'SIGNUP' or 'RESET_PASSWORD'.
    """
    from apps.accounts.models import User

    user = User.objects.get(id=user_id)

    # TODO: Implement email sending logic
    # from common.email import mail_service
    # if purpose == "SIGNUP":
    #     mail_service.send_signup_otp(user, otp_code)
    # elif purpose == "RESET_PASSWORD":
    #     mail_service.send_reset_password_otp(user, otp_code)

    logger.info(f"OTP email sent to {user.email}: {otp_code} ({purpose})")


@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_admin_invitation_email_task(user_id, invitation_link):
    """
    Send an admin invitation email with a link to set password.
    """
    from apps.accounts.models import User

    user = User.objects.get(id=user_id)

    # TODO: Implement email sending logic
    logger.info(f"Admin invitation sent to {user.email}: {invitation_link}")


@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_admin_removed_email_task(user_id):
    """
    Notify a user that their admin access has been removed.
    """
    from apps.accounts.models import User

    user = User.objects.get(id=user_id)

    # TODO: Implement email sending logic
    logger.info(f"Admin removed notification sent to {user.email}")


@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_admin_restored_email_task(user_id):
    """
    Notify a user that their admin access has been restored.
    """
    from apps.accounts.models import User

    user = User.objects.get(id=user_id)

    # TODO: Implement email sending logic
    logger.info(f"Admin restored notification sent to {user.email}")
'''
    path = Path("apps/accounts/tasks.py")
    path.write_text(content, encoding="utf-8")
    print("[green]✔ Created apps/accounts/tasks.py[/green]")


def create_accounts_views():
    """Create accounts/views/ directory with auth, password, profile views."""

    # views/__init__.py
    init_content = """from apps.accounts.views.auth import (
    SignUpView,
    SignInView,
    VerifyEmailView,
    ResendVerificationCodeView,
    RefreshAccessTokenView,
    SocialLoginView,
)
from apps.accounts.views.password import (
    ForgotPasswordRequestView,
    VerifyResetCodeView,
    ResetPasswordView,
    ChangePasswordView,
)
from apps.accounts.views.profile import MyAccountView
"""
    Path("apps/accounts/views/__init__.py").write_text(init_content, encoding="utf-8")

    # views/auth.py
    auth_content = '''import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import EmailOTP, User
from apps.accounts.serializers.auth import (
    SignUpSerializer,
    SignInSerializer,
    VerifyEmailSerializer,
    ResendCodeSerializer,
    SocialLoginSerializer,
)

logger = logging.getLogger(__name__)


class SignUpView(APIView):
    """
    Register a new user with email and password.
    
    POST /api/auth/sign-up
    {
        "email": "user@example.com",
        "full_name": "John Doe",
        "password": "securepassword123"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Generate OTP
        otp_code = EmailOTP.generate_code()
        otp = EmailOTP.objects.create(user=user, code=otp_code, purpose=EmailOTP.Purpose.SIGNUP, expires_at=EmailOTP.default_expiry(minutes=5))
        
        # TODO: Send OTP email via Celery task
        # from apps.accounts.tasks import send_otp_email_task
        # send_otp_email_task.delay(str(user.id), otp_code, "SIGNUP")
        
        return Response({"success": True, "message": "Verification code sent to your email.", "data": {"email": user.email}}, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    """
    Verify email with OTP code.
    
    POST /api/auth/verify-email
    {
        "email": "user@example.com",
        "code": "123456"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        
        user = User.objects.get(email=email)
        
        # Find valid OTP
        otp = EmailOTP.objects.filter(user=user, code=code, purpose=EmailOTP.Purpose.SIGNUP, is_used=False, expires_at__gt=timezone.now()).first()
        
        if not otp:
            return Response({"success": False, "message": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark user as verified
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        
        # Mark OTP as used
        otp.mark_as_used()
        
        return Response({"success": True, "message": "Email verified successfully."}, status=status.HTTP_200_OK)


class ResendVerificationCodeView(APIView):
    """
    Resend verification code.
    
    POST /api/auth/resend-code
    {
        "email": "user@example.com"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        
        # Invalidate old OTPs
        EmailOTP.objects.filter(user=user, purpose=EmailOTP.Purpose.SIGNUP, is_used=False).update(is_used=True)
        
        # Generate new OTP
        otp_code = EmailOTP.generate_code()
        otp = EmailOTP.objects.create(user=user, code=otp_code, purpose=EmailOTP.Purpose.SIGNUP, expires_at=EmailOTP.default_expiry(minutes=5))
        
        # TODO: Send OTP email via Celery task
        
        return Response({"success": True, "message": "Verification code resent."}, status=status.HTTP_200_OK)


class SignInView(APIView):
    """
    Sign in with email and password.
    
    POST /api/auth/sign-in
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data["user"]
        
        # Generate tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "success": True, "message": "Login successful.",
            "data": {
                "access": str(refresh.access_token), "refresh": str(refresh),
                "user": {"id": str(user.id), "email": user.email, "full_name": user.full_name, "role": user.role, "avatar": user.avatar.url if user.avatar else None},
            },
        }, status=status.HTTP_200_OK)


class RefreshAccessTokenView(APIView):
    """
    Refresh access token.
    
    POST /api/auth/refresh-token
    {
        "refresh": "your-refresh-token"
    }
    """
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({"success": False, "message": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken(refresh_token)
            return Response({"success": True, "data": {"access": str(refresh.access_token), "refresh": str(refresh)}}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)


class SocialLoginView(APIView):
    """
    Social login (Google, Facebook, Apple).
    
    POST /api/auth/social-login
    {
        "provider": "google",
        "access_token": "social-access-token"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider = serializer.validated_data["provider"]
        social_id = serializer.validated_data["social_id"]
        
        # TODO: Implement social login logic
        # 1. Verify token with provider
        # 2. Find or create user by social_id + provider
        # 3. Generate JWT tokens
        
        return Response({"success": False, "message": "Social login not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)
'''
    Path("apps/accounts/views/auth.py").write_text(auth_content, encoding="utf-8")

    # views/password.py
    password_content = '''from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import EmailOTP, User
from apps.accounts.serializers.password import (
    ForgotPasswordSerializer,
    VerifyResetCodeSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)


class ForgotPasswordRequestView(APIView):
    """
    Request password reset code.
    
    POST /api/auth/forgot-password
    {
        "email": "user@example.com"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        
        # Generate OTP
        otp_code = EmailOTP.generate_code()
        otp = EmailOTP.objects.create(user=user, code=otp_code, purpose=EmailOTP.Purpose.RESET_PASSWORD, expires_at=EmailOTP.default_expiry(minutes=5))
        
        # TODO: Send OTP email via Celery task
        
        return Response({"success": True, "message": "Reset code sent to your email."}, status=status.HTTP_200_OK)


class VerifyResetCodeView(APIView):
    """
    Verify password reset code.
    
    POST /api/auth/verify-reset-code
    {
        "email": "user@example.com",
        "code": "123456"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        
        user = User.objects.get(email=email)
        
        otp = EmailOTP.objects.filter(user=user, code=code, purpose=EmailOTP.Purpose.RESET_PASSWORD, is_used=False, expires_at__gt=timezone.now()).first()
        
        if not otp:
            return Response({"success": False, "message": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)
        
        import uuid
        reset_token = str(uuid.uuid4())
        
        user.reset_secret_key = reset_token
        user.save(update_fields=["reset_secret_key"])
        
        otp.mark_as_used()
        
        return Response({"success": True, "message": "Code verified. Use the reset token to change password.", "data": {"reset_token": reset_token}}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Reset password with token.
    
    POST /api/auth/reset-password
    {
        "reset_token": "uuid-token",
        "new_password": "newsecurepassword123"
    }
    """
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data["reset_token"]
        new_password = serializer.validated_data["new_password"]
        
        # Find user by reset token
        user = User.objects.filter(reset_secret_key=reset_token).first()
        
        if not user:
            return Response({"success": False, "message": "Invalid reset token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save(update_fields=["password"])
        
        return Response({"success": True, "message": "Password reset successfully."}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    Change password (authenticated).
    
    POST /api/auth/change-password
    {
        "old_password": "oldpassword",
        "new_password": "newpassword"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]
        
        user = request.user
        
        if not user.check_password(old_password):
            return Response({"success": False, "message": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save(update_fields=["password"])
        
        return Response({"success": True, "message": "Password changed successfully."}, status=status.HTTP_200_OK)
'''
    Path("apps/accounts/views/password.py").write_text(password_content, encoding="utf-8")

    # views/profile.py
    profile_content = '''from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.serializers.profile import UserProfileSerializer


class MyAccountView(APIView):
    """
    Get or update current user's profile.
    
    GET /api/auth/my-account
    PUT /api/auth/my-account
    {
        "full_name": "John Doe",
        "bio": "Software developer",
        "website": "https://example.com"
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"success": True, "message": "Profile updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
'''
    Path("apps/accounts/views/profile.py").write_text(profile_content, encoding="utf-8")

    print("[green]✔ Created apps/accounts/views/[/green]")


def create_accounts_serializers():
    """Create accounts/serializers/ directory with auth, password, profile serializers."""

    # serializers/__init__.py
    init_content = """from apps.accounts.serializers.auth import (
    SignUpSerializer,
    SignInSerializer,
    VerifyEmailSerializer,
    ResendCodeSerializer,
    SocialLoginSerializer,
)
from apps.accounts.serializers.password import (
    ForgotPasswordSerializer,
    VerifyResetCodeSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)
from apps.accounts.serializers.profile import UserProfileSerializer
"""
    Path("apps/accounts/serializers/__init__.py").write_text(init_content, encoding="utf-8")

    # serializers/auth.py
    auth_content = """from rest_framework import serializers

from apps.accounts.models import User


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "full_name", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            password=validated_data["password"],
        )
        return user


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email", "").lower()
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")

        if user.is_blocked:
            raise serializers.ValidationError("Account is blocked.")

        data["user"] = user
        return data


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SocialLoginSerializer(serializers.Serializer):
    PROVIDER_CHOICES = [("google", "Google"), ("facebook", "Facebook"), ("apple", "Apple")]
    
    provider = serializers.ChoiceField(choices=PROVIDER_CHOICES)
    social_id = serializers.CharField()
"""
    Path("apps/accounts/serializers/auth.py").write_text(auth_content, encoding="utf-8")

    # serializers/password.py
    password_content = """from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
"""
    Path("apps/accounts/serializers/password.py").write_text(password_content, encoding="utf-8")

    # serializers/profile.py
    profile_content = """from rest_framework import serializers

from apps.accounts.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "avatar",
            "avatar_url",
            "bio",
            "website",
            "role",
            "push_notification",
            "daily_reminder",
            "reminder_time",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["id", "email", "role", "is_verified", "created_at"]

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
"""
    Path("apps/accounts/serializers/profile.py").write_text(profile_content, encoding="utf-8")

    print("[green]✔ Created apps/accounts/serializers/[/green]")


def create_accounts_urls():
    """Create accounts/urls.py with all auth endpoints."""
    content = """from django.urls import path

from apps.accounts.views.auth import (
    SignUpView,
    SignInView,
    VerifyEmailView,
    ResendVerificationCodeView,
    RefreshAccessTokenView,
    SocialLoginView,
)
from apps.accounts.views.password import (
    ForgotPasswordRequestView,
    VerifyResetCodeView,
    ResetPasswordView,
    ChangePasswordView,
)
from apps.accounts.views.profile import MyAccountView

urlpatterns = [
    # Public Auth
    path("/sign-up", SignUpView.as_view(), name="auth-sign-up"),
    path("/verify-email", VerifyEmailView.as_view(), name="auth-verify-email"),
    path("/resend-code", ResendVerificationCodeView.as_view(), name="auth-resend-code"),
    path("/sign-in", SignInView.as_view(), name="auth-sign-in"),
    path("/forgot-password", ForgotPasswordRequestView.as_view(), name="auth-forgot-password"),
    path("/verify-reset-code", VerifyResetCodeView.as_view(), name="auth-verify-reset-code"),
    path("/reset-password", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("/refresh-token", RefreshAccessTokenView.as_view(), name="auth-refresh-token"),
    path("/social-login", SocialLoginView.as_view(), name="auth-social-login"),
    # Authenticated
    path("/change-password", ChangePasswordView.as_view(), name="auth-change-password"),
    path("/my-account", MyAccountView.as_view(), name="auth-my-account"),
]
"""
    path = Path("apps/accounts/urls.py")
    path.write_text(content, encoding="utf-8")
    print("[green]✔ Created apps/accounts/urls.py[/green]")


def create_accounts_apps():
    """Create accounts/apps.py."""
    content = """from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Accounts"
"""
    path = Path("apps/accounts/apps.py")
    path.write_text(content, encoding="utf-8")
    print("[green]✔ Created apps/accounts/apps.py[/green]")


def create_accounts_admin():
    """Create accounts/admin.py."""
    content = """from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import AdminSectionPermission, EmailOTP, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ["email", "full_name", "role", "is_verified", "is_blocked", "is_active"]
    list_filter = ["role", "is_verified", "is_blocked", "is_active"]
    search_fields = ["email", "full_name"]
    ordering = ["-created_at"]
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name", "avatar", "bio", "website")}),
        ("Roles & Status", {"fields": ("role", "is_verified", "is_blocked", "is_active", "is_staff")}),
        ("Settings", {"fields": ("push_notification", "daily_reminder", "reminder_time")}),
        ("Social Login", {"fields": ("social_id", "social_provider")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2", "role"),
        }),
    )


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ["user", "purpose", "code", "is_used", "expires_at"]
    list_filter = ["purpose", "is_used"]
    search_fields = ["user__email"]


@admin.register(AdminSectionPermission)
class AdminSectionPermissionAdmin(admin.ModelAdmin):
    list_display = ["section", "access"]
    list_filter = ["section", "access"]
"""
    path = Path("apps/accounts/admin.py")
    path.write_text(content, encoding="utf-8")
    print("[green]✔ Created apps/accounts/admin.py[/green]")


def create_accounts_tests():
    """Create accounts/tests.py - fresh default Django test file."""
    content = """from django.test import TestCase

# Create your tests here.
"""
    path = Path("apps/accounts/tests.py")
    path.write_text(content, encoding="utf-8")
    print("[green]✔ Created apps/accounts/tests.py[/green]")


def create_accounts_init():
    """Create accounts/__init__.py."""
    path = Path("apps/accounts/__init__.py")
    path.touch()
    print("[green]✔ Created apps/accounts/__init__.py[/green]")


def create_accounts_migrations_init():
    """Create accounts/migrations/__init__.py."""
    path = Path("apps/accounts/migrations/__init__.py")
    path.touch()
    print("[green]✔ Created apps/accounts/migrations/__init__.py[/green]")


def update_project_settings(name: str):
    """Add accounts app to INSTALLED_APPS in settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    # Check if already installed
    if "apps.accounts" in content:
        print("[yellow]Warning: apps.accounts already in INSTALLED_APPS. Skipping.[/yellow]")
        return True

    # Add to INSTALLED_APPS
    content = content.replace(
        "'rest_framework_simplejwt',",
        "'rest_framework_simplejwt',\n    'rest_framework_simplejwt.token_blacklist',",
    )

    content = content.replace(
        "'rest_framework_simplejwt.token_blacklist',",
        "'rest_framework_simplejwt.token_blacklist',\n    'apps.accounts',",
    )

    # Add AUTH_USER_MODEL if not present
    if "AUTH_USER_MODEL" not in content:
        content += "\n\n# Custom User Model\nAUTH_USER_MODEL = 'accounts.User'\n"

    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added accounts app to {name}/settings.py[/green]")
    return True


def update_project_urls(name: str):
    """Add accounts URLs to project urls.py."""
    urls_path = Path(f"{name}/urls.py")
    if not urls_path.exists():
        print(f"[red]Error: {name}/urls.py not found.[/red]")
        return False

    content = urls_path.read_text(encoding="utf-8")

    # Check if already configured
    if "apps.accounts.urls" in content:
        print("[yellow]Warning: accounts URLs already configured. Skipping.[/yellow]")
        return True

    # Add import
    content = content.replace("from django.urls import path", "from django.urls import path, include")

    # Add URL pattern
    content = content.replace(
        "urlpatterns = [",
        'urlpatterns = [\n    path("/api/auth", include("apps.accounts.urls")),',
    )

    urls_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added accounts URLs to {name}/urls.py[/green]")
    return True


def create_accounts_app(name: str):
    """Main function to create complete accounts app."""
    # Check if accounts app already exists
    accounts_path = Path("apps") / "accounts"
    if accounts_path.exists():
        print("[red]Error: App 'accounts' already exists at apps/accounts.[/red]")
        print("[yellow]Use 'djboost startapp <name>' for other app names.[/yellow]")
        import typer

        raise typer.Exit(1)

    print(f"\n[bold green]🚀 Creating accounts app for: {name}[/bold green]\n")

    # Create directories
    print("[cyan]📁 Creating directory structure...[/cyan]")
    create_accounts_directories()

    # Create files
    print("[cyan]📝 Creating models...[/cyan]")
    create_accounts_models()

    print("[cyan]🔐 Creating permissions...[/cyan]")
    create_accounts_permissions()

    print("[cyan]📋 Creating Celery tasks...[/cyan]")
    create_accounts_tasks()

    print("[cyan]👁️  Creating views...[/cyan]")
    create_accounts_views()

    print("[cyan]📦 Creating serializers...[/cyan]")
    create_accounts_serializers()

    print("[cyan]🔗 Creating URLs...[/cyan]")
    create_accounts_urls()

    print("[cyan]⚙️  Creating app config...[/cyan]")
    create_accounts_apps()

    print("[cyan]🛡️  Creating admin...[/cyan]")
    create_accounts_admin()

    print("[cyan]🧪 Creating tests...[/cyan]")
    create_accounts_tests()

    print("[cyan]📄 Creating init files...[/cyan]")
    create_accounts_init()
    create_accounts_migrations_init()

    # Update project files
    print("[cyan]⚙️  Updating project settings...[/cyan]")
    update_project_settings(name)

    print("[cyan]🔗 Updating project URLs...[/cyan]")
    update_project_urls(name)

    print()
    print("[bold green]✅ Accounts app created successfully![/bold green]")
    print()
    print("[cyan]API Endpoints:[/cyan]")
    print("  POST /api/auth/sign-up          - Register new user")
    print("  POST /api/auth/verify-email     - Verify email with OTP")
    print("  POST /api/auth/resend-code      - Resend verification code")
    print("  POST /api/auth/sign-in          - Login with email/password")
    print("  POST /api/auth/forgot-password  - Request password reset")
    print("  POST /api/auth/verify-reset-code - Verify reset code")
    print("  POST /api/auth/reset-password   - Reset password")
    print("  POST /api/auth/refresh-token    - Refresh JWT token")
    print("  POST /api/auth/social-login     - Social login (Google/Facebook/Apple)")
    print("  POST /api/auth/change-password  - Change password (authenticated)")
    print("  GET  /api/auth/my-account       - Get profile (authenticated)")
    print("  PUT  /api/auth/my-account       - Update profile (authenticated)")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Run [bold]python manage.py makemigrations accounts[/bold]")
    print("  2. Run [bold]python manage.py migrate[/bold]")
    print("  3. Run [bold]python manage.py createsuperuser[/bold]")
    print("  4. Run [bold]python manage.py runserver[/bold]")
