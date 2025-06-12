from django.urls import path
from jobcard_business.views import CandidateListForEmployer

urlpatterns = [
    path("employer/jobs/<int:job_id>/candidates/",CandidateListForEmployer.as_view(),name="employer-job-candidates"),
]
