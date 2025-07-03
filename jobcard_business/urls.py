# urls.py
from django.urls import path
from . import views, institute_api

urlpatterns = [
    path('employer/job-list/', views.JobListBusinessAPIView.as_view(), name='employer-applications'),
    path('employer/dashboard/', views.EmployerDashboardAPIView.as_view(), name='employer-dashboard'),
    path('list/student/<int:job_id>/', views.JobApplicationListBusinessAPI.as_view(), name='business-job-applications'),
    
    
    path('institution-jobs/', institute_api.JobListInstituteAPI.as_view(), name='institution-job-list'),
    path('applied/student/<int:job_id>/', institute_api.JobApplicationListInstituteAPIView.as_view(), name='Institution-job-applications'),
]