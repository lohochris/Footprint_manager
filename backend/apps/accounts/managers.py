from __future__ import annotations

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for :class:`User`.

    Provides ``create_user`` and ``create_superuser`` helpers that require an
    email address and generate a UUID primary key.
    """

    def _create_user(self, email: str | None = None, password: str | None = None, **extra_fields):
        from .models.user import User
        username = extra_fields.pop("username", None)
        if not email:
            email = extra_fields.pop("email", None) or username
            if email and "@" not in email:
                email = f"{email}@example.com"
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if not isinstance(user, User):
            raise TypeError("Expected User model instance")
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str | None = None, password: str | None = None, **extra_fields):
        from .models.user import User
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("account_status", User.Status.PENDING)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str | None = None, password: str | None = None, **extra_fields):
        from .models.user import User
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("account_status", User.Status.ACTIVE)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)
