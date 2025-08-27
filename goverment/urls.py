from django.urls import path
from . import views




urlpatterns = [
    
    path("jobs-list/", views.JobListGovermentAPIView.as_view(), name="job-list"),
    path('applications/<int:job_id>/', views.JobApplicationListOfStudentGoverment.as_view(), name='job-applications-by-job'),
    path("government/dashboard/", views.DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
    path('placed-students/', views.PlacedStudentListAPIView.as_view(), name='placed-student-list'),
    path('job/count-by-business/', views.JobCountByBusinessAPIView.as_view()),
    path("member-applications/", views.MemberJobApplicationsAPIView.as_view(), name="member-applications"),
    
]