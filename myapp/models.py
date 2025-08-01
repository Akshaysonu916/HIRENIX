from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    is_company = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)  # NEW

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)