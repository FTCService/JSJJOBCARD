from django.urls import path
from . import views, job_mitra_api
urlpatterns = [
    path("jobs-list/post/", views.JobListCreateAPIView.as_view(), name="job-list-create"),
    path("jobs-details/<int:id>/", views.JobDetailAPIView.as_view(), name="job-detail"),
    # path("applications/", JobApplicationListAPIView.as_view(), name="job-applications"),
    # ✅ Job Mitra API
    path("jobmitra/jobs/<str:location>/", job_mitra_api.JobMitraJobListView.as_view(), name="jobmitra-jobs"),
    path("jobmitra/applications/", job_mitra_api.JobMitraApplicationListAPIView.as_view(), name="jobmitra-applications"),
    path("jobmitra/apply/<int:job_id>/", job_mitra_api.JobMitraApplyAPIView.as_view(), name="jobmitra-apply-job"),
    
]

