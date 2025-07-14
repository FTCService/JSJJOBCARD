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
from jobcard_business import models, serializers


class JobListBusinessAPIView(APIView):
    """
    API to list all jobs or create a new job post.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings.",
        responses={200: JobpostSerializer(many=True)},tags=["Business"]
    )
    def get(self, request):
        try:
            business = request.user.business_id
            if not business:
                return Response({
                    "success": False,
                    "message": "Authenticated user is not associated with a business."
                }, status=status.HTTP_400_BAD_REQUEST)
            jobs = models.Job.objects.filter(business_id=business)
            serializer = JobpostSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobDetailBusinessAPIView(APIView):
    """
    API to retrieve, update, or delete a job post by ID.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a job by its ID.",
        responses={200: JobpostSerializer()},tags=["Business"]
    )
    def get(self, request, job_id):
        try:
            job = models.Job.objects.get(id=job_id)
            serializer = JobpostSerializer(job)
            return Response({
                "success": True,
                "message": "Job retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobApplicationListBusinessAPI(APIView):
    """
    API to list all applications for jobs posted by the authenticated business.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all job applications received for this business.",
        responses={200: serializers.JobApplicationListForBusinessSerializer(many=True)},tags=["Business"]
    )
    def get(self, request, job_id):
        try:
            # business_id = request.user.business_id
            # if not business_id:
            #     return Response({
            #         "success": False,
            #         "message": "Authenticated user is not associated with a business."
            #     }, status=status.HTTP_400_BAD_REQUEST)
           
            applications = models.JobApplication.objects.filter(job_id=job_id)
            serializer = serializers.JobApplicationListForBusinessSerializer(applications, many=True)

            return Response({
                "success": True,
                "message": "Job applications retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
class EmployerDashboardAPIView(APIView):
    """
    API for employer dashboard summary:
    - Total jobs posted
    - Total applications received
    - Total students placed
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get employer dashboard stats: total jobs, applications, and placed students.",
        responses={200: 'Dashboard Stats'},
        tags=["Business"]
    )
    def get(self, request):
        try:
            business_id = request.user.business_id
            if not business_id:
                return Response({
                    "success": False,
                    "message": "Authenticated user is not associated with a business."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get all jobs for this business
            job_ids = models.Job.objects.filter(business_id=business_id).values_list('id', flat=True)

            # Total jobs
            total_jobs = job_ids.count()

            # Total applications across all jobs
            total_applications = models.JobApplication.objects.filter(job_id__in=job_ids).count()

            # Total placed students (assuming status = 'placed' or 'selected')
            total_placed = models.JobApplication.objects.filter(
                job_id__in=job_ids,
                status__in=["placed", "selected"]
            ).count()

            return Response({
                "success": True,
                "message": "Dashboard data retrieved successfully.",
                "data": {
                    "total_jobs": total_jobs,
                    "total_applications": total_applications,
                    "total_placed_students": total_placed
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "Server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BusinessJobListCreateAPIView(APIView):
    """
    API to list or create job posts for the authenticated business.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all job posts created by the authenticated business.",
        responses={200: JobpostSerializer()},tags=["Business"]
    )
    def get(self, request):
        """
        Returns all job posts for the currently authenticated business.
        """
        try:
            business_id = getattr(request.user, 'business_id', None)
            if not business_id:
                return Response({"error": "Business ID not found for the user."}, status=400)

            jobs = Job.objects.filter(business_id=business_id)
            serializer = JobpostSerializer(jobs, many=True)

            return Response({
                "success": True,
                "message": "Business job list retrieved successfully.",
                "business_id": business_id,  # Include business_id in response
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new job post for the authenticated business.",
        request_body=JobpostSerializer,
        responses={200: JobpostSerializer()},tags=["Business"]
    )
    def post(self, request):
        try:
            business_id = getattr(request.user, 'business_id', None)
            if not business_id:
                return Response({"error": "Business ID not found for the user."}, status=400)

            data = request.data.copy()
            data['business_id'] = business_id  # Inject business ID
            serializer = JobpostSerializer(data=data)

            if serializer.is_valid():
                job = serializer.save()
                return Response({
                    "success": True,
                    "message": "Job posted successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "success": False,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)