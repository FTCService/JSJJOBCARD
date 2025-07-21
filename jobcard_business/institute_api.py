from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.timezone import now
from jobcard_business.authentication import SSOBusinessTokenAuthentication
from jobcard_staff.serializers import JobpostSerializer
from jobcard_business import models
from jobcard_member.serializers import JobApplicationListSerializer
from helpers.utils import get_member_details_by_card



class JobListInstituteAPI(APIView):
    """
    API to list all jobs or create a new job post.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings.",
        responses={200: JobpostSerializer(many=True)},tags=["Institute"]
    )
    def get(self, request):
        try:
            jobs = models.Job.objects.all()
            total_jobs = jobs.count()
            serializer = JobpostSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "total_jobs":total_jobs,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
class JobApplicationListInstituteAPIView(APIView):
    """
    API to list all applications for jobs posted by the authenticated business,
    along with job details.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all job applications received for this business, including job details.",
        responses={200: JobApplicationListSerializer(many=True)},
        tags=["Institute"]
    )
    def get(self, request, job_id):
        try:
            business_id = request.user.business_id
            if not business_id:
                return Response({
                    "success": False,
                    "message": "Authenticated user is not associated with a business."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch applications
            applications = models.JobApplication.objects.filter(job_id=job_id, institute_id=business_id)
            application_serializer = JobApplicationListSerializer(applications, many=True)

            # ✅ Fetch job details (ignore business filter)
            try:
                job = models.Job.objects.get(id=job_id)
                job_serializer = JobpostSerializer(job)
                job_data = job_serializer.data
            except models.Job.DoesNotExist:
                job_data = None

            return Response({
                "success": True,
                "message": "Job applications retrieved successfully.",
                "job_details": job_data,
                "data": application_serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "Server error.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
