from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser,EmployeeProfile, CompanyProfile, HRProfile



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

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ["profile_picture", "bio", "location", "birthdate"]

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ["logo", "company_name", "industry", "website", "about"]

class HRProfileForm(forms.ModelForm):
    class Meta:
        model = HRProfile
        fields = ["profile_picture", "bio", "hr_department"]