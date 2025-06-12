from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from jobcard_staff.models import JobApplication, Job
from .serializers import CandidateSummarySerializer
from .authentication import SSOBusinessTokenAuthentication
from rest_framework.permissions import IsAuthenticated

class CandidateListForEmployer(generics.ListAPIView):
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CandidateSummarySerializer

    @swagger_auto_schema(
        operation_summary="View candidates who applied for a job",
        operation_description="Employers can see candidate name and card number for their job postings.",
        manual_parameters=[
            openapi.Parameter(
                'job_id',
                openapi.IN_PATH,
                description="The Job ID for which to list applicants",
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: CandidateSummarySerializer(many=True)}
    )
    def get_queryset(self):
        job_id = self.kwargs['job_id']
        # Confirm that the job belongs to the logged-in employer
        Job.objects.get(id=job_id, employer_id=self.request.user.employer_id)
        return JobApplication.objects.filter(job_id=job_id).only("candidate_name", "member_id")