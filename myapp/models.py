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
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    skills = models.CharField(max_length=255, blank=True, null=True)  # could store comma-separated tags
    education = models.TextField(blank=True, null=True)  # or make a separate Education model
    work_experience = models.TextField(blank=True, null=True)
    domain = models.CharField(max_length=100, blank=True, null=True)  # e.g., Django, React, etc.
    

    def __str__(self):
        return f"Employee Profile - {self.user.username}"


class CompanyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # new
    contact_number = models.CharField(max_length=20, blank=True, null=True)  # new
    website = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Company Profile - {self.company_name}"

    def total_jobs_posted(self):
        return self.jobs.count()  # assumes Job model has ForeignKey to CompanyProfile

    def active_jobs(self):
        return self.jobs.filter(is_active=True)

    def hr_members(self):
        return self.user.hrprofile_set.all()  # assumes HRProfile has FK to company

    def total_candidates_hired(self):
        # adjust depending on your hiring model
        return self.jobs.filter(status="hired").count()


class HRProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="hr_profiles/", null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    hr_department = models.CharField(max_length=255, blank=True, null=True)
    company = models.ForeignKey('CompanyProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name="hr_profiles")
    business_contact_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"HR Profile - {self.user.username}"