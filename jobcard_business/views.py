from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from django.utils.timezone import now
from jobcard_staff.models import JobApplication, Job
from .serializers import CandidateSummarySerializer, InstitutionJobSerializer, JobApplicationCountSerializer
from jobcard_business.authentication import SSOBusinessTokenAuthentication


class EmployerJobApplicationsView(generics.ListAPIView):
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CandidateSummarySerializer

    @swagger_auto_schema(
        operation_summary="List candidates for a job",
        operation_description="Employers can view name and member card of candidates who applied to their job posting.",
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
        return JobApplication.objects.filter(job_id=job_id).only("candidate_name", "member_card")
    
class InstitutionJobListView(APIView):
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Institution: View Jobs under this college",
        responses={200: InstitutionJobSerializer(many=True)},
        tags=["Institution"]
    )
    def get(self, request):
        institution = getattr(request.user, 'institution', None)

        if not institution:
            return Response({
                "success": False,
                "message": "User is not associated with any institution"
            }, status=400)

        jobs = Job.objects.filter(institution=institution).order_by('-created_at')
        serializer = InstitutionJobSerializer(jobs, many=True)
        return Response({
            "success": True,
            "message": "Jobs fetched successfully",
            "data": serializer.data
        }, status=200)
        
class InstitutionJobApplicationsCountView(APIView):
    permission_classes = [IsAuthenticated]  # Adjust as needed

    @swagger_auto_schema(
        operation_description="List jobs posted by the logged-in college user with total applicants per job.",
        responses={200: JobApplicationCountSerializer(many=True)}
    )
    def get(self, request):
        # Filter jobs posted by this college user, using staff_email or another field
        jobs = Job.objects.filter(staff_email=request.user.email)
        serializer = JobApplicationCountSerializer(jobs, many=True)
        return Response(serializer.data)