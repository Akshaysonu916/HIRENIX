from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    is_company = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)  # NEW

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)


    def get_profile(self):
        if self.is_employee:
            return getattr(self, 'employeeprofile', None)
        elif self.is_company:
            return getattr(self, 'companyprofile', None)
        elif self.is_hr:
            return getattr(self, 'hrprofile', None)
        return None

    


# profile models
class EmployeeProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Employee Profile - {self.user.username}"


class CompanyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Company Profile - {self.company_name}"


class HRProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="hr_profiles/", null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    hr_department = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"HR Profile - {self.user.username}"