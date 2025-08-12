from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import login, logout , authenticate
from .forms import CustomLoginForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm  
from django.contrib.auth.decorators import login_required
from django.utils import timezone



# login and logout views

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)  # ✅ MUST pass request
        if form.is_valid():
            user = form.get_user()  # ✅ Correct way to get the user
            login(request, user)

            # ✅ Redirect based on role
            if user.is_employee:
                return redirect('candidate_home')
            elif user.is_hr:
                return redirect('hr_dashboard')
            elif user.is_company:
                return redirect('company_dashboard')
            elif user.is_superuser:
                return redirect('admin_dashboard')  # ✅ Admin dashboard
            else:
                messages.warning(request, "User role not defined.")
                return redirect('login')
        else:
            messages.error(request, "Invalid credentials.")
            print("Form errors:", form.errors)  # ✅ DEBUGGING
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# =============================
# ✅ SIGNUP VIEWS
# =============================

def choose_signup(request):
    return render(request, 'choose_signup.html')


def employee_signup(request):
    if request.method == 'POST':
        form = EmployeeSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_employee = True
            user.save()
            login(request, user)
            return redirect('login')  # ✅ Correct name here
    else:
        form = EmployeeSignUpForm()

    return render(request, 'registration/employee_signup.html', {'form': form})


def company_signup(request):
    if request.method == 'POST':
        form = CompanySignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_company = True
            user.save()
            login(request, user)
            return redirect('company_dashboard')
    else:
        form = CompanySignUpForm()

    return render(request, 'registration/company_signup.html', {'form': form})


# =============================
# ✅ HOME / DASHBOARD VIEWS
# =============================

@login_required
def home_view(request):
    if hasattr(request.user, 'is_employee') and request.user.is_employee:
        return render(request, 'home.html', {'user': request.user})
    return HttpResponseForbidden("Access denied.")


@login_required()
def hr_dashboard(request):
    if hasattr(request.user, 'is_hr') and request.user.is_hr:
        return render(request, 'hr_dashboard.html')
    return HttpResponseForbidden("Access denied.")


@login_required
def company_dashboard(request):
    if hasattr(request.user, 'is_company') and request.user.is_company:
        return render(request, 'company_dashboard.html')
    return HttpResponseForbidden("Access denied.")

@login_required
def candidate_home(request):
    return render(request, 'home.html')



#==============================
# ✅ HR ADDING VIEWS
#==============================
@login_required
def add_hr_view(request):
    if request.method == 'POST':
        form = HRSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_dashboard')  # or a success page
    else:
        form = HRSignUpForm()
    return render(request, 'add_hr.html', {'form': form})



#==============================
# ✅ admin VIEWS
#==============================

@login_required
def admin_dashboard(request):
    total_users = CustomUser.objects.count()
    new_signups = CustomUser.objects.filter(date_joined__gte='2025-08-01').count()  # Example recent month/range
    # Replace with your logic for sessions/logs.
    active_sessions = 5  # Placeholder
    recent_logs = [
        {'timestamp': '2025-08-07 10:25', 'message': 'User JohnDoe logged in.'},
        {'timestamp': '2025-08-07 09:05', 'message': 'Admin updated settings.'},
    ]
    context = {
        'total_users': total_users,
        'new_signups': new_signups,
        'active_sessions': active_sessions,
        'recent_logs': recent_logs,
    }
    return render(request, 'admin_dashboard.html', context)



#==============================
# ✅ profile VIEWS
#==============================

@login_required
def profile_view(request):
    profile = request.user.get_profile()

    # Prepare skills list (for employee profiles)
    skills_list = []
    if hasattr(profile, "skills") and profile.skills:
        skills_list = [
            skill.strip() for skill in profile.skills.split(",") if skill.strip()
        ]

    # Base context
    context = {
        "profile": profile,
        "skills_list": skills_list
    }

    # Employee profile
    if request.user.is_employee:
        template = "employee_profile.html"

    # Company profile
    elif request.user.is_company:
        template = "company_profile.html"

    # HR profile
    elif request.user.is_hr:
        template = "hr_profile.html"

        # ===== Placeholder data until you add models =====
        jobs = []                  # Replace with Job.objects.filter(hr=request.user)
        candidates = []            # Replace with CandidateInterview.objects.filter(interviewer=request.user)
        upcoming_interviews = []   # Replace with candidates.filter(date__gte=timezone.now())

        stats = {
            "total_hired": 0,       # Replace with candidates.filter(status="Hired").count()
            "total_shortlisted": 0, # Replace with candidates.filter(status="Shortlisted").count()
            "total_rejected": 0,    # Replace with candidates.filter(status="Rejected").count()
        }
        # ==================================================

        # Add to context for HR template
        context.update({
            "jobs": jobs,
            "candidates": candidates,
            "upcoming_interviews": upcoming_interviews,
            "stats": stats
        })

    # Fallback generic profile
    else:
        template = "generic_profile.html"

    return render(request, template, context)

@login_required
def profile_edit(request):
    """Edit profile for Employee, Company, or HR user."""
    profile = request.user.get_profile()

    # Select form class based on user type
    form_map = {
        "employee": EmployeeProfileForm,
        "company": CompanyProfileForm,
        "hr": HRProfileForm,
    }
    user_type = (
        "employee" if request.user.is_employee else
        "company" if request.user.is_company else
        "hr" if request.user.is_hr else
        None
    )

    if not user_type:
        messages.error(request, "Invalid user type.")
        return redirect("profile")

    FormClass = form_map[user_type]

    if request.method == "POST":
        form = FormClass(
            request.POST, 
            request.FILES, 
            instance=profile, 
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FormClass(instance=profile, user=request.user)

    context = {
        "form": form,
        "user_type": user_type,
    }
    return render(request, "edit_profile.html", context)