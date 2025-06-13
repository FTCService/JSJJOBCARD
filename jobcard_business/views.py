from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from django.utils.timezone import now
from jobcard_staff.models import JobApplication, Job
from .serializers import CandidateSummarySerializer, JobPublicSerializer
from jobcard_business.authentication import SSOBusinessTokenAuthentication


class EmployerJobApplicationsView(generics.ListAPIView):
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CandidateSummarySerializer

    @swagger_auto_schema(
        operation_summary="List candidates for a job",
        operation_description="Employers can view name and member ID of candidates who applied to their job posting.",
        manual_parameters=[
            openapi.Parameter(
                'job_id',
                openapi.IN_PATH,
                description="Job ID to view applicants for",
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: CandidateSummarySerializer(many=True)}
    )
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        Job.objects.get(id=job_id, employer_id=self.request.user.employer_id)
        return JobApplication.objects.filter(job_id=job_id).only("candidate_name", "member_id")

class JobMitraJobListView(APIView):
    """
    Authenticated Job Mitra users see active job listings
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Job Mitra: View active job listings",
        operation_description="Returns jobs to authenticated Job Mitra users only.",
        responses={200: JobPublicSerializer(many=True)},
        tags=["Job Mitra"]
    )
    def get(self, request):
        try:
            # Optional: Add check for job mitra user type, if such role exists
            # if not request.user.is_jobmitra:
            #     return Response({"success": False, "message": "Unauthorized"}, status=403)

            jobs = Job.objects.filter(application_end_date__gte=now()).order_by('-created_at')
            serializer = JobPublicSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": "Job Mitra job listings retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "Error retrieving jobs.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)