from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from jobcard_business.models import Job, JobApplication
from . import serializers
from .authentication import SSOGovernmentTokenAuthentication
from jobcard_member.models import MbrDocuments
from jobcard_staff.serializers import JobpostSerializer,JobApplicationStaffViewSerializer


class JobListGovermentAPIView(APIView):
    """
    API to list all jobs 
    """
    authentication_classes = [SSOGovernmentTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings.",
        responses={200: JobpostSerializer(many=True)},tags=["Goverment"]
    )
    def get(self, request):
        try:
            jobs = Job.objects.all()
            serializer = JobpostSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

        

class JobApplicationListOfStudentGoverment(APIView):
    """
    Goverment can view job applications or update their status.
    """
    authentication_classes = [SSOGovernmentTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all student applications for a specific job ID.",
        responses={200: JobApplicationStaffViewSerializer(many=True)},
        tags=["Goverment"]
    )
    def get(self, request, job_id):
        try:
            applications = JobApplication.objects.filter(job_id=job_id)
            serializer = JobApplicationStaffViewSerializer(applications, many=True)
            return Response({
                "success": True,
                "message": "Applications retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)