from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import Issue, Officer, ReportedUser
from .forms import CitizenRegistrationForm, AuthorityRegistrationForm
from .ai_prioritization import compute_severity, calculate_priority

# ✅ Home Page View
def home(request):
    return render(request, "reports/base.html")

# ✅ Citizen Login
def citizen_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("citizen_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "reports/citizen_login.html")

# ✅ Citizen Dashboard
@login_required
def citizen_dashboard(request):
    citizen_issues = Issue.objects.filter(user=request.user)
    return render(request, "reports/citizen_dashboard.html", {"issues": citizen_issues})

# ✅ Track Issue
@login_required
def track_issue(request):
    issues = Issue.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reports/track_issue.html', {"issues": issues})

# ✅ Get Issue Status
@login_required
def get_issue_status(request, issue_id=None):
    try:
        if issue_id:
            issue = Issue.objects.get(id=issue_id, user=request.user)
        else:
            issues = Issue.objects.filter(user=request.user).values('id', 'title', 'status', 'created_at')
            return JsonResponse(list(issues), safe=False)

        data = {
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity,
            "date": issue.created_at.strftime("%Y-%m-%d"),
            "image": issue.image.url if issue.image else None,
            "status": issue.status
        }
        return JsonResponse(data)
    except Issue.DoesNotExist:
        return JsonResponse({"error": "Issue not found"}, status=404)

@login_required
def reported_issues(request):
    # ✅ Show all issues the user has ever reported (even duplicates)
    issues = Issue.objects.filter(reported_user_entries__user=request.user).distinct()
    return render(request, 'reports/reported_issues.html', {'issues': issues})


# ✅ Report Issue with Semantic Deduplication + AI Priority
@login_required
def report_issue(request):
    if request.method == "POST":
        user = request.user
        location_name = request.POST.get("location_name", "").strip()
        description = request.POST.get("description", "").strip()
        latitude = float(request.POST.get("latitude"))
        longitude = float(request.POST.get("longitude"))
        image = request.FILES.get("image")

        if not location_name or not description:
            return JsonResponse({"error": "Location and description are required."}, status=400)

        nearby_issues = Issue.objects.filter(
            Q(latitude__range=(latitude - 0.0002, latitude + 0.0002)) &
            Q(longitude__range=(longitude - 0.0002, longitude + 0.0002))
        )

        for issue in nearby_issues:
            similarity = issue.compute_description_similarity(description)
            if similarity >= 0.75:  # 75% semantic similarity threshold
                if ReportedUser.objects.filter(issue=issue, user=user).exists():
                    return JsonResponse({"error": "You have already reported this issue."}, status=400)
                issue.report_count = F("report_count") + 1
                issue.save(update_fields=["report_count"])
                issue.refresh_from_db()
                ReportedUser.objects.create(issue=issue, user=user)
                issue.update_priority()
                return JsonResponse({
                    "message": "Issue already exists. Report count incremented.",
                    "report_count": issue.report_count,
                    "priority": issue.priority_score
                })

        new_issue = Issue.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            description=description,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            image=image if image else None,
            report_count=1
        )
        ReportedUser.objects.create(issue=new_issue, user=user)
        new_issue.update_priority()

        return JsonResponse({"message": "New issue reported.", "issue_id": new_issue.id})

    return JsonResponse({"error": "Invalid request method."}, status=400)

# ✅ Report Issue Page
@login_required
def index(request):
    return render(request, "reports/index.html")

# ✅ Authority Login
@csrf_exempt
def authority_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("authority_dashboard")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "reports/authority_login.html")

# ✅ Authority Dashboard
@login_required
def authority_dashboard(request):
    issues = Issue.objects.all().order_by('-priority_score', '-report_count')

    # ✅ Ensure priorities are freshly recalculated
    for i in issues:
        i.update_priority()

    return render(request, "reports/authority_dashboard.html", {"reported_issues": issues})


# ✅ Citizen Registration
def citizen_register(request):
    if request.method == "POST":
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('citizen_login')
        else:
            messages.error(request, "Registration failed.")
    else:
        form = CitizenRegistrationForm()

    return render(request, 'reports/citizen_register.html', {'form': form})

# ✅ Authority Registration
def authority_register(request):
    if request.method == "POST":
        form = AuthorityRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect("authority_login")
        else:
            messages.error(request, "Registration failed.")
    else:
        form = AuthorityRegistrationForm()

    return render(request, "reports/authority_register.html", {"form": form})

# ✅ AI-Prioritized Issues List
@login_required
def prioritized_issues(request):
    calculate_priority()
    issues = Issue.objects.order_by('-priority_score')
    return render(request, 'reports/prioritized_issues.html', {'issues': issues})

# ✅ Officer Login
def officer_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("officer_dashboard")
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, "reports/officer_login.html")

# ✅ Officer Dashboard
@login_required
def officer_dashboard(request):
    officer = get_object_or_404(Officer, user=request.user)
    issues = Issue.objects.filter(assigned_officer=officer)
    return render(request, "reports/officer_dashboard.html", {"issues": issues})

# ✅ Issue Detail View
@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    return render(request, "reports/issue_detail.html", {"issue": issue})

# ✅ Update Progress View
@login_required
def update_progress(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == "POST":
        progress = request.POST.get("progress_percentage")
        status = request.POST.get("status")
        work_image = request.FILES.get("work_image")

        issue.progress_percentage = int(progress)
        issue.status = status

        if work_image:
            issue.work_images = work_image

        issue.save()
        messages.success(request, "Issue updated successfully!")
        return redirect("officer_dashboard")

    return redirect("officer_dashboard")

# ✅ Logout
def logout_user(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect("home")

# ✅ Trending Issues Dashboard
@login_required
def trending_issues(request):
    trending_issues = Issue.objects.order_by('-report_count')[:10]
    
    # Refresh priority before showing
    for issue in trending_issues:
        issue.update_priority()

    return render(request, "reports/trending_issues.html", {"trending_issues": trending_issues})
