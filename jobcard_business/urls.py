# urls.py
from django.urls import path
from .views import EmployerJobApplicationsView, JobMitraJobListView

urlpatterns = [
    path('employer/applications/', EmployerJobApplicationsView.as_view(), name='employer-applications'),
    path('job-mitra/jobs/', JobMitraJobListView.as_view(), name='job-mitra-job-list'),
]
