from django.urls import path
from .views import (
    home, index,citizen_register, authority_register,
    citizen_login, authority_login, citizen_dashboard, authority_dashboard,
    prioritized_issues, report_issue,logout_user,trending_issues,
    officer_login, officer_dashboard, issue_detail, track_issue,update_progress,reported_issues
)

urlpatterns = [
    path("", home, name="home"),
    path("index/", index, name="index"),
    path("report_issue/", report_issue, name="report_issue"),
    #path("submit-issue/", submit_issue, name="submit_issue"),
    path("citizen/register/", citizen_register, name="citizen_register"),
    path("authority/register/", authority_register, name="authority_register"),
    path("citizen/login/", citizen_login, name="citizen_login"),
    path("authority/login/", authority_login, name="authority_login"),
    path("citizen/dashboard/", citizen_dashboard, name="citizen_dashboard"),
    path("authority/dashboard/", authority_dashboard, name="authority_dashboard"),
    path("authority/dashboard/prioritized_issues/", prioritized_issues, name="prioritized_issues"),
    path("trending-issues/", trending_issues, name="trending_issues"),
    path("officer-login/", officer_login, name="officer_login"),
    path("officer-dashboard/", officer_dashboard, name="officer_dashboard"),
    path("issue/<int:issue_id>/", issue_detail, name="issue_detail"),
    path('reported-issues/', reported_issues, name='reported_issues'),
    path("track/", track_issue, name="track_issue"),  # ✅ Proper import added
    path("update-progress/<int:issue_id>/", update_progress, name="update_progress"),
    path("logout/", logout_user, name="logout"),
]
