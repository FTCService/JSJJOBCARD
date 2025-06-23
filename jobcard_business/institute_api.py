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
            serializer = JobpostSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
class JobApplicationListInstituteAPIView(APIView):
    """
    API to list all applications for jobs posted by the authenticated business.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all job applications received for this business.",
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
           
            applications = models.JobApplication.objects.filter(job_id=job_id, institute_id=business_id)
            serializer = JobApplicationListSerializer(applications, many=True)

            return Response({
                "success": True,
                "message": "Job applications retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)