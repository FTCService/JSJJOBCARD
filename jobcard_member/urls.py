from django.urls import path
from jobcard_member import views

urlpatterns = [
    # # Member documents upload/update
    path("documents/", views.MbrDocumentsAPI.as_view(), name="member-documents"),
    path('job/list/', views.JoblistAPIView.as_view(), name='job-list'),
    path('job/details/<int:job_id>/', views.JobDetailAPIView.as_view(), name='job-detail'),
    path('apply/job/', views.JobApplyAPIView.as_view(), name='job-apply'),

]
