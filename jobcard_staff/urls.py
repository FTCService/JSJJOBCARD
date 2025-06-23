from django.urls import path
from . import views, job_mitra_api
urlpatterns = [
    path("jobs-list/post/", views.JobListCreateAPIView.as_view(), name="job-list-create"),
    path("jobs-details/<int:id>/", views.JobDetailAPIView.as_view(), name="job-detail"),
    path('job-applications/<int:job_id>/', views.JobApplicationListOfStudent.as_view(), name='job-applications-by-job'),
    path('staff/member-documents/<str:card_number>/', views.MbrDocumentsAPI.as_view(), name='member-documents'),
    
    
    
    path('job_mitra/applied/list/<int:job_id>/', job_mitra_api.ApplicationListOfStudent.as_view(), name='job_mitra-applied-list'),
]



