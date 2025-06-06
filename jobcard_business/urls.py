from django.urls import path
from .views import DocumentByCardNumber, JobListView, JobPostView

urlpatterns = [
    path('api/hr/member-documents/', DocumentByCardNumber.as_view(), name='get-documents-by-card-number'),
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/post/', JobPostView.as_view(), name='post-job'),
]
