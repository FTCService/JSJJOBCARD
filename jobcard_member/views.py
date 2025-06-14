from django.conf import settings
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from helpers.utils import get_member_details_by_mobile, get_member_details_by_card
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from .authentication import SSOMemberTokenAuthentication
from . import serializers, models
from jobcard_business.models import JobApplication, Job
from jobcard_staff.serializers import JobpostSerializer




class MbrDocumentsAPI(APIView):
    """
    API to handle Member Documents (Retrieve, Upload).
    """
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all documents of the authenticated member",
        responses={200: serializers.MbrDocumentsSerializer()},tags=["Member"]
    )
    def get(self, request):
        """
        Get all documents for the authenticated member.
        """
        
        documents = models.MbrDocuments.objects.filter(card_number=request.user.mbrcardno).first()

        if not documents:
            return Response({"success": True, "data": {}}, status=status.HTTP_200_OK)  # Return empty dict instead of 404
        
        serializer = serializers.MbrDocumentsSerializer(documents)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Upload or update document URLs for the authenticated member",
        request_body=serializers.MbrDocumentsSerializer,
        responses={200: serializers.MbrDocumentsSerializer()},tags=["Member"]
    )
    def post(self, request):
        """
        Upload or update document URLs for the authenticated member.
        Automatically saves card_number from request.user.
        """
        card_number = request.user.mbrcardno  # Get member's card number

        # Get or create the document instance for this card number
        documents, created = models.MbrDocuments.objects.get_or_create(card_number=card_number)

        serializer = serializers.MbrDocumentsSerializer(documents, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(card_number=card_number)  # Ensure the card_number is always set
            return Response({"success": True, "message": "Documents updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class JoblistAPIView(APIView):
    """
    API for a member list of job.
    """
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings.",
        responses={200: JobpostSerializer(many=True)},tags=["Member"]
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
        
        
    
class JobApplyAPIView(APIView):
    """
    API for a member to apply for a job.
    """
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get all jobs applied by the member.",
        responses={200: serializers.JobApplicationListSerializer(many=True)},
        tags=["Member"]
    )
    def get(self, request):
        try:
            member_card = request.user.mbrcardno  # from SSO
            applications = JobApplication.objects.filter(member_card=member_card).select_related('job').order_by('-applied_at')
            serializer = serializers.JobApplicationListSerializer(applications, many=True)
            return Response({
                "success": True,
                "message": "Applied jobs retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        operation_description="Apply for a job by providing job ID, resume, and optional cover letter.",
        request_body=serializers.JobApplicationCreateSerializer,
        responses={201: "Application submitted successfully."},
        tags=["Member"]
    )
    def post(self, request):
        try:
            serializer = serializers.JobApplicationCreateSerializer(data=request.data)
            if serializer.is_valid():
                job_id = serializer.validated_data.get('job')
                job = Job.objects.get(id=job_id.id)

                member_card = request.user.mbrcardno  # assuming this comes from your SSO system
               
                # Check if already applied
                if JobApplication.objects.filter(job=job, member_card=member_card).exists():
                    return Response({
                        "success": False,
                        "message": "You have already applied to this job."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Save application
                JobApplication.objects.create(
                    job=job,
                    member_card=member_card,
                    institute_id=serializer.validated_data.get('institute_id', ''),
                    cover_letter=serializer.validated_data.get('cover_letter', ''),
                    resume=serializer.validated_data.get('resume')
                )

                return Response({
                    "success": True,
                    "message": "Application submitted successfully."
                }, status=status.HTTP_201_CREATED)

            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Job.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid job ID."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    
# class JobApplicationCreateView(generics.CreateAPIView):
#     authentication_classes = [SSOMemberTokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     serializer_class = JobApplicationSerializer
   

#     @swagger_auto_schema(
#         operation_summary="Student Apply for a Job",
#         operation_description="Student applies for a job. Returns only application number and member card number.",
#         request_body=JobApplicationSerializer
#     )
#     def post(self, request):
#         member_card = request.user.mbrcardno  # 👈 get from auth token
#         data = request.data.copy()
        

#         serializer = self.get_serializer(data=data)
#         if serializer.is_valid():
#             job_application = serializer.save()

#             # ✅ Generate application number
#             year = datetime.now().year
#             loc = job_application.location.upper().replace(" ", "")[:3]
#             mem = member_card.upper()[:4]
#             app_number = f"{year}-{loc}-{mem}-{job_application.id:04d}"

#             # ✅ Save application number
#             job_application.application_number = app_number
#             job_application.save()

#             return Response({
#                 "application_number": app_number,
#                 "member_card_number": member_card
#             }, status=status.HTTP_201_CREATED)

#         return Response({
#             "success": False,
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
