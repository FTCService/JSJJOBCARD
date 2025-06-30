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
            
            
            
            
import requests
from django.conf import settings


class DashboardSummaryAPIView(APIView):
    """
    Dashboard API: View all registered institutes, companies, jobs, and placed students.
    """

    @swagger_auto_schema(
        operation_description="Dashboard summary showing total registered institutes, companies, jobs, and placed students.",
        responses={
            200: openapi.Response(
                description="Dashboard summary response",
                examples={
                    "application/json": {
                        "success": True,
                        "total_institute": 2,
                        "total_company": 10,
                        "job_titles": 5,
                        "placed_students": 3
                    }
                }
            ),
            500: openapi.Response(description="Server error")
        },
        tags=["Government"]
    )
    def get(self, request):
        try:
            # 1️⃣ Request institute and company data from AUTH server
            auth_response = requests.get(f"{settings.AUTH_SERVER_URL}/admin/dashboard/business-summary/")
            if auth_response.status_code != 200:
                return Response({
                    "success": False,
                    "message": "Failed to fetch business data from auth server."
                }, status=500)

            auth_data = auth_response.json()
            total_institute = auth_data.get("institutes", 0)
            total_company = auth_data.get("companies", 0)

            # 2️⃣ Jobs
            jobs = Job.objects.count()

            # 3️⃣ Placed Students (status = 'selected')
            selected_apps = JobApplication.objects.filter(status='selected').count()

            return Response({
                "success": True,
                "total_institute": total_institute,
                "total_company": total_company,
                "job_titles": jobs,
                "placed_students": selected_apps
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "Server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class JobCountByBusinessAPIView(APIView):
    """
    Returns number of jobs posted by a business.
    """

    def get(self, request):
        business_id = request.GET.get("business_id")
        if not business_id:
            return Response({"job_count": 0}, status=400)

        count = Job.objects.filter(business_id=business_id).count()
        return Response({"job_count": count}, status=200)
