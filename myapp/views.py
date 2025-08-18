from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import login, logout , authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm  
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Count
from collections import defaultdict
from django.db.models import Q
from django.utils.timezone import now


# login and logout views

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ✅ Redirect based on role
            if getattr(user, 'is_employee', False):
                return redirect('candidate_home')
            elif getattr(user, 'is_hr', False):
                return redirect('hr_dashboard')
            elif getattr(user, 'is_company', False):
                return redirect('company_dashboard')
            elif user.is_superuser:
                return redirect('admin_dashboard')
            else:
                messages.warning(request, "User role not defined.", extra_tags="global")
                return redirect('login')
        else:
            # Only login errors → tagged with "login"
            messages.error(request, "Invalid username or password.", extra_tags="login")
            print("Form errors:", form.errors)
    else:
        form = AuthenticationForm()

    # --- ✅ Separate login errors from other messages ---
    storage = messages.get_messages(request)  # consumes all queued messages
    all_msgs = list(storage)

    login_msgs = [
        m for m in all_msgs
        if ('login' in m.tags and m.level == messages.ERROR)
    ]
    keep_msgs = [m for m in all_msgs if m not in login_msgs]

    # ✅ Re-add non-login messages so they appear later (not lost)
    for m in keep_msgs:
        messages.add_message(request, m.level, m.message, extra_tags=m.tags)

    return render(request, 'login.html', {
        'form': form,
        'login_messages': login_msgs,  # 👈 only login errors
    })

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
    # Allow only company users
    if not getattr(request.user, 'is_company', False):
        return HttpResponseForbidden("Access denied.")

    # Fetch jobs posted by the logged-in company + application counts
    jobs = (
        Job.objects.filter(company=request.user)
        .annotate(applicant_count=Count("applications"))  # 'applications' is related_name in JobApplication model
        .order_by("-created_at")  # newest first
    )

    return render(request, "company_dashboard.html", {
        "jobs": jobs,
        "total_jobs": jobs.count()
    })

@login_required
def candidate_home(request):
    return render(request, 'home.html')



#==============================
# ✅ HR VIEWS
#==============================
@login_required
def add_hr_view(request):
    if request.method == 'POST':
        form = HRSignUpForm(request.POST)
        if form.is_valid():
            # Save the HR user
            user = form.save(commit=False)
            user.is_hr = True
            user.save()

            # ✅ Create or update HRProfile and link to logged-in company
            company = request.user.companyprofile
            hr_profile, created = HRProfile.objects.get_or_create(user=user)
            hr_profile.company = company
            hr_profile.save()

            return redirect('company_dashboard')  # success page
    else:
        form = HRSignUpForm()

    return render(request, 'add_hr.html', {'form': form})



@login_required
def hr_list(request):
    if hasattr(request.user, "companyprofile"):  # use correct related name
        company = request.user.companyprofile
        hrs = HRProfile.objects.filter(company=company)
    else:
        hrs = HRProfile.objects.none()  # safer than []
    
    return render(request, "hr_list.html", {"hrs": hrs})


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


User = get_user_model()

# Check if current user is admin
def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin)
def manage_users(request):
    user_type = request.GET.get("type")

    # Start with all non-admins
    users = User.objects.exclude(is_superuser=True)

    # Apply filtering based on boolean fields
    if user_type == "employee":
        users = users.filter(is_employee=True)
    elif user_type == "company":
        users = users.filter(is_company=True)
    elif user_type == "hr":
        users = users.filter(is_hr=True)

    return render(
        request,
        "manage_users.html",
        {"users": users, "selected_type": user_type}
    )

@user_passes_test(is_admin)
def view_user_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    profile = user.get_profile()
    return render(request, "view_user_profile.html", {"user": user, "profile": profile})


@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f"User '{username}' deleted successfully.")
    return redirect("manage_users")


@login_required
@user_passes_test(is_admin)
def admin_job_list(request):
    q = request.GET.get('q', '').strip()
    jobs = Job.objects.select_related('company').order_by('-created_at')

    if q:
        jobs = jobs.filter(title__icontains=q)

    # If you’re using soft delete, hide inactive ones by default (toggle via query if needed)
    show_inactive = request.GET.get('show_inactive') == '1'
    if not show_inactive:
        jobs = jobs.filter(is_active=True)

    paginator = Paginator(jobs, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/admin_job_list.html', {
        'page_obj': page_obj,
        'q': q,
        'show_inactive': show_inactive,
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.delete()  # Permanently remove from the database
    messages.success(request, 'Job permanently deleted.')

    # Redirect back to the jobs list (keeping pagination & filters if any)
    next_url = request.POST.get('next') or reverse('admin_manage_jobs')
    return redirect(next_url)



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



#==============================
# ✅ job VIEWS
#==============================

def is_company(user):
    """Helper to check if the logged-in user is a company."""
    return hasattr(user, 'companyprofile')  # Adjust if you have a profile model


@login_required
def job_list(request):
    if not is_company(request.user):
        messages.error(request, "You are not authorized to view job listings.")
        return redirect("home")

    # ✅ Step 1: Deactivate expired jobs before listing
    deactivate_expired_jobs()

    # ✅ Step 2: Get all jobs posted by this company
    job_qs = Job.objects.filter(company=request.user).order_by('-created_at')

    # ✅ Step 3: Paginate results
    paginator = Paginator(job_qs, 10)  # 10 jobs per page
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)

    return render(request, "jobs/job_list.html", {"jobs": jobs})


@login_required
def job_create(request):
    if not is_company(request.user):
        messages.error(request, "Only company accounts can post jobs.")
        return redirect("home")

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect(reverse("job_list"))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm()

    return render(request, "jobs/job_form.html", {"form": form, "title": "Post a New Job"})


@login_required
def job_edit(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect(reverse("job_list"))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm(instance=job)

    return render(request, "jobs/job_form.html", {"form": form, "title": "Edit Job"})


@login_required
def job_delete(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user)
    job.delete()
    messages.success(request, "Job deleted successfully!")
    return redirect(reverse("job_list"))


def deactivate_expired_jobs():
    """Mark expired jobs as inactive in the DB."""
    today = timezone.now().date()
    Job.objects.filter(
        is_active=True,
        application_deadline__lt=today
    ).update(is_active=False)

@login_required
def browse_jobs(request):
    # ✅ Step 1: Deactivate expired jobs in DB
    deactivate_expired_jobs()

    today = timezone.now().date()

    # ✅ Step 2: Get only active & not expired jobs
    jobs = Job.objects.filter(
        is_active=True
    ).filter(
        Q(application_deadline__isnull=True) | Q(application_deadline__gte=today)
    ).order_by('-created_at')

    # ✅ Get filter parameters from GET request
    search_query = request.GET.get('q', '').strip()
    job_type = request.GET.get('job_type', '')
    experience_level = request.GET.get('experience_level', '')

    # ✅ Apply search filter
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(company__username__icontains=search_query)  # assuming company = CustomUser
        )

    # ✅ Apply job type filter
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    # ✅ Apply experience level filter
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)

    return render(request, "jobs/browse_jobs.html", {
        "jobs": jobs,
        "search_query": search_query,
        "selected_job_type": job_type,
        "selected_experience": experience_level,
    })

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)

    # Check if the logged-in user has already applied
    already_applied = JobApplication.objects.filter(
        job=job,
        applicant=request.user
    ).exists()

    return render(request, "jobs/job_detail.html", {
        "job": job,
        "already_applied": already_applied,
        "today": now().date(),
    })

@login_required
@require_POST
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect("job_detail", job_id=job.id)

    # Ensure employee profile exists
    employee_profile = getattr(request.user, "employeeprofile", None)
    if not employee_profile:
        messages.error(request, "You must complete your profile before applying.")
        return redirect("job_detail", job_id=job.id)

    # Ensure resume exists
    if not employee_profile.resume:
        messages.error(request, "Please upload your resume in your profile before applying.")
        return redirect("job_detail", job_id=job.id)

    # Create application using the resume from profile
    JobApplication.objects.create(
        job=job,
        applicant=request.user,
        resume=employee_profile.resume
    )

    messages.success(request, "Your application has been submitted successfully!")
    return redirect("job_detail", job_id=job.id)


@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user)
    applicants = job.applications.select_related("applicant")
    return render(request, "jobs/view_applicants.html", {
        "job": job,
        "applicants": applicants
    })


@login_required
def manage_applications(request):
    if not getattr(request.user, 'is_company', False):
        return HttpResponseForbidden("Access denied.")

    # Get all applications for jobs posted by this company
    applications = JobApplication.objects.filter(
        job__company=request.user
    ).select_related("job", "applicant").order_by("-applied_at")

    # ✅ Group applications by job domain
    grouped_apps = defaultdict(list)
    for app in applications:
        grouped_apps[app.job.domain].append(app)

    return render(request, "jobs/manage_applications.html", {
        "grouped_apps": dict(grouped_apps)  # pass grouped dictionary to template
    })

#==============================
# ✅ Application VIEWS
#==============================
@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job')
    return render(request, "my_applications.html", {"applications": applications})