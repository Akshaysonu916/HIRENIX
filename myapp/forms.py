from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser,EmployeeProfile, CompanyProfile, HRProfile
from django.contrib.auth import get_user_model



#signup forms
class EmployeeSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class CompanySignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

# Custom login form  
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full p-3 border rounded-md',
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-3 border rounded-md',
        'placeholder': 'Password',
    }))


# hr adding form
class HRSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_hr = True
        if commit:
            user.save()
        return user
    


# profile forms

User = get_user_model()

class EmployeeProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Enter your email address")

    class Meta:
        model = EmployeeProfile
        fields = [
            "profile_picture",
            "bio",
            "location",
            "birthdate",
            "resume",
            "skills",
            "education",
            "work_experience",
            "domain",
            "email",  # <-- not actually in EmployeeProfile, handled separately
        ]
        widgets = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "Write something about yourself..."}),
            "skills": forms.TextInput(attrs={"placeholder": "e.g., Python, Django, React"}),
            "education": forms.Textarea(attrs={"rows": 3, "placeholder": "Your educational background..."}),
            "work_experience": forms.Textarea(attrs={"rows": 3, "placeholder": "Your work experience..."}),
            "domain": forms.TextInput(attrs={"placeholder": "Your primary domain/specialization"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Save email to User model
            user = profile.user
            user.email = self.cleaned_data['email']
            user.save()
        return profile

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ["logo", "company_name", "industry", "website", "about"]

class HRProfileForm(forms.ModelForm):
    class Meta:
        model = HRProfile
        fields = ["profile_picture", "bio", "hr_department"]