from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from jobcard_business.models import Job, JobApplication
from . import serializers
from .authentication import SSOUserTokenAuthentication
from jobcard_member.models import MbrDocuments
from jobcard_member.serializers import MbrDocumentsSerializer
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
        
        
        

class JobApplicationListOfStudent(APIView):
    """
    Staff can view job applications or update their status.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all student applications for a specific job ID.",
        responses={200: serializers.JobApplicationStaffViewSerializer(many=True)},
        tags=["Staff"]
    )
    def get(self, request, job_id):
        try:
            applications = JobApplication.objects.filter(job_id=job_id)
            serializer = serializers.JobApplicationStaffViewSerializer(applications, many=True)
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

    # @swagger_auto_schema(
    #     operation_description="Update the status of a specific job application by ID.",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         required=['status'],
    #         properties={
    #             'status': openapi.Schema(
    #                 type=openapi.TYPE_STRING,
    #                 enum=['applied', 'under_review', 'shortlisted', 'rejected', 'selected'],
    #                 description="New status of the job application"
    #             )
    #         }
    #     ),
    #     manual_parameters=[
    #         openapi.Parameter(
    #             'application_id',
    #             openapi.IN_PATH,
    #             description="ID of the JobApplication to update",
    #             type=openapi.TYPE_INTEGER,
    #             required=True
    #         )
    #     ],
    #     responses={200: openapi.Response("Status updated")},
    #     tags=["Staff"]
    # )
    # def put(self, request, job_id):
    #     try:
    #         application_id = request.data.get('application_id')
    #         new_status = request.data.get('status')

    #         if not application_id or not new_status:
    #             return Response({
    #                 "success": False,
    #                 "message": "Both 'application_id' and 'status' are required."
    #             }, status=status.HTTP_400_BAD_REQUEST)

    #         job_application = JobApplication.objects.filter(id=application_id, job_id=job_id).first()

    #         if not job_application:
    #             return Response({
    #                 "success": False,
    #                 "message": "Job application not found."
    #             }, status=status.HTTP_404_NOT_FOUND)

    #         job_application.status = new_status
    #         job_application.save()

    #         return Response({
    #             "success": True,
    #             "message": "Status updated successfully.",
    #             "application_id": job_application.id,
    #             "new_status": job_application.status
    #         }, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         return Response({
    #             "success": False,
    #             "message": "Failed to update status.",
    #             "error": str(e)
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
            
            
class MbrDocumentsAPI(APIView):
    """
    Staff can view documents submitted by candidates.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all candidate documents filtered by member card number.",
        manual_parameters=[
            openapi.Parameter(
                'card_number',
                openapi.IN_PATH,
                description="Candidate's member card number",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: openapi.Response(
            description="List of submitted documents",
            schema=MbrDocumentsSerializer(many=True)
        )},
        tags=["Staff"]
    )
    def get(self, request, card_number):
        try:
           
            documents = MbrDocuments.objects.filter(card_number=card_number)
            

            serializer = MbrDocumentsSerializer(documents, many=True)

            return Response({
                "success": True,
                "message": "Documents retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while retrieving documents.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
