# urls.py
from django.urls import path
from .views import EmployerJobApplicationsView, InstitutionJobListView, InstitutionJobApplicationsCountView


urlpatterns = [
    path('employer/applications/', EmployerJobApplicationsView.as_view(), name='employer-applications'),
    path('institution-jobs/', InstitutionJobListView.as_view(), name='institution-job-list'),
    path('Institution/job-applications/', InstitutionJobApplicationsCountView.as_view(), name='Institution-job-applications'),
]