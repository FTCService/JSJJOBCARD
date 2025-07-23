# urls.py
from django.urls import path
from . import views, institute_api

urlpatterns = [
    path('employer/job-list/', views.JobListBusinessAPIView.as_view(), name='employer-applications'),
    path('employer/dashboard/', views.EmployerDashboardAPIView.as_view(), name='employer-dashboard'),
    path('job-details/<int:job_id>/', views.JobDetailBusinessAPIView.as_view(), name='job-details'),
    path('list/student/<int:job_id>/', views.JobApplicationListBusinessAPI.as_view(), name='business-job-applications'),
    path('documents/details/<int:card_number>/', views.GetMemberDocumentsAPIView.as_view(), name='get-member-documents'),
    
    path('institution-jobs/', institute_api.JobListInstituteAPI.as_view(), name='institution-job-list'),
    path('applied/student/<int:job_id>/', institute_api.JobApplicationListInstituteAPIView.as_view(), name='Institution-job-applications'),
]