from django.urls import path
from . import views
from .views import (
    JobPostListView,
    JobPostDetailView,
    JobApplicationCreateView,
    MbrDocumentsAPI
)

urlpatterns = [
    # Member documents upload/update
    path("documents/", MbrDocumentsAPI.as_view(), name="member-documents"),

    # Job post APIs for students
    path("jobs/", JobPostListView.as_view(), name="job-post-list"),
    path("jobs/<int:id>/", JobPostDetailView.as_view(), name="job-post-detail"),
    
    # Student job application API
    path("jobs/apply/", JobApplicationCreateView.as_view(), name="job-apply"),
]
