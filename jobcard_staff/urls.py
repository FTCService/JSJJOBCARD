from django.urls import path
from . import views
urlpatterns = [
    path("jobs-list/post/", views.JobListCreateAPIView.as_view(), name="job-list-create"),
    path("jobs-details/<int:id>/", views.JobDetailAPIView.as_view(), name="job-detail"),
    # path("applications/", JobApplicationListAPIView.as_view(), name="job-applications"),
    
]

