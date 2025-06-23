# urls.py
from django.urls import path
from . import views, institute_api
from .views import MbrDocumentsByCardAPI


urlpatterns = [
    path('employer/job-list/', views.JobListBusinessAPIView.as_view(), name='employer-applications'),
    
    
    
    path('institution-jobs/', institute_api.JobListInstituteAPI.as_view(), name='institution-job-list'),
    path('applied/student/<int:job_id>/', institute_api.JobApplicationListInstituteAPIView.as_view(), name='Institution-job-applications'),
    
    path('member-documents/<int:card_number>/', MbrDocumentsByCardAPI.as_view(), name='hr-member-documents'),
]