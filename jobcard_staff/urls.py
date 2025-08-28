from django.urls import path
from . import views, job_mitra_api
urlpatterns = [
    path("jobs-list/post/", views.JobListCreateAPIView.as_view(), name="job-list-create"),
    path("jobs-details/<int:id>/", views.JobDetailAPIView.as_view(), name="job-detail"),
    path('job-applications/<int:job_id>/', views.JobApplicationListOfStudent.as_view(), name='job-applications-by-job'),
    path('staff/member-documents/<str:card_number>/', views.MbrDocumentsAPI.as_view(), name='member-documents'),
    
    path('document-verification/list/', views.StaffDocumentVerificationListAPIView.as_view(), name='staff-document-requests'),
    path('document/verification/status/<str:card_number>/', views.StaffUpdateDocumentStatusAPIView.as_view(), name='staff-update-document-status'),
    path('hr-feedbacks/', views.HRFeedbackListAPI.as_view(), name='hr-feedback-list'),
    
    
    path('job_mitra/applied/list/<int:job_id>/', job_mitra_api.ApplicationListOfStudent.as_view(), name='job_mitra-applied-list'),
    path('jobmitra/member-details/', job_mitra_api.GetMemberDetailsByCardApi.as_view(), name='get-member-details'),
    path('jobmitra/apply-for-member/', job_mitra_api.ApplyJobForMemberAPIView.as_view(), name='apply-job-for-member'),
    
]



