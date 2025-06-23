from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from jobcard_business.models import Job
from jobcard_staff import serializers
from .authentication import SSOUserTokenAuthentication


class JobListCreateAPIView(APIView):
    """
    API to list all jobs or create a new job post.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings.",
        responses={200: serializers.JobpostSerializer(many=True)},tags=["Staff"]
    )
    def get(self, request):
        try:
            jobs = Job.objects.all()
            serializer = serializers.JobpostSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new job post.",
        request_body=serializers.JobpostSerializer,
        responses={201: serializers.JobpostSerializer},tags=["Staff"]
    )
    def post(self, request):
        try:
            serializer = serializers.JobpostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Job created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "success": False,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobDetailAPIView(APIView):
    """
    API to retrieve, update, or delete a job post by ID.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a job by its ID.",
        responses={200: serializers.JobpostSerializer()},tags=["Staff"]
    )
    def get(self, request, id):
        try:
            job = Job.objects.get(id=id)
            serializer = serializers.JobpostSerializer(job)
            return Response({
                "success": True,
                "message": "Job retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_description="Update a job post by its ID.",
        request_body=serializers.JobpostSerializer,
        responses={200: serializers.JobpostSerializer()},
        tags=["Staff"]
    )
    def put(self, request, id):
        try:
            job = Job.objects.get(id=id)
            serializer = serializers.JobpostSerializer(job, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Job updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            return Response({"success": False, "message": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        

# class JobApplicationListAPIView(APIView):
#     """
#     Staff can view all job applications or filter by job ID.
#     Shows each application's generated application number.
#     """
#     authentication_classes = [SSOUserTokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Retrieve job applications. Optionally filter by job ID.",
#         manual_parameters=[
#             openapi.Parameter(
#                 'job_id',
#                 openapi.IN_QUERY,
#                 description="Filter applications by job ID",
#                 type=openapi.TYPE_INTEGER
#             )
#         ],
#         responses={200: JobApplicationSerializer(many=True)}
#     )
#     def get(self, request):
#         try:
#             job_id = request.query_params.get("job_id")
#             if job_id:
#                 applications = JobApplication.objects.filter(job_id=job_id)
#             else:
#                 applications = JobApplication.objects.all()
            
#             serializer = JobApplicationSerializer(applications, many=True)
#             return Response({
#                 "success": True,
#                 "message": "Applications retrieved successfully.",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({
#                 "success": False,
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# ✅ JOB MITRA: List Jobs by Location
