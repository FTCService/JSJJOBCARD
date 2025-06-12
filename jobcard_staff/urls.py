from django.urls import path
from .views import JobListCreateAPIView, JobDetailAPIView, JobApplicationListAPIView, MbrDocumentsAPI

urlpatterns = [
    path("jobs/", JobListCreateAPIView.as_view(), name="job-list-create"),
    path("jobs/<int:id>/", JobDetailAPIView.as_view(), name="job-detail"),
    path("applications/", JobApplicationListAPIView.as_view(), name="job-applications"),
    path("documents/", MbrDocumentsAPI.as_view(), name="candidate-documents"),
]
