from django.urls import path
from . import views




urlpatterns = [
    
    path("jobs-list/", views.JobListGovermentAPIView.as_view(), name="job-list"),
    path('applications/<int:job_id>/', views.JobApplicationListOfStudentGoverment.as_view(), name='job-applications-by-job'),
    
]