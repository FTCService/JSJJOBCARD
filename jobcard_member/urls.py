from django.urls import path
from jobcard_member import views
from jobcard_staff.models import JobApplication

urlpatterns = [
    # Member documents upload/update
    path("documents/", views.MbrDocumentsAPI.as_view(), name="member-documents"),
    path('apply/', views.JobApplicationCreateView.as_view(), name='job-apply'),


]
