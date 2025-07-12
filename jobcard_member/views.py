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
import os
from urllib.parse import urlparse
import re
from helpers.email import send_template_email


class MbrDocumentsAPI(APIView):
    """
    API to handle Member Documents (Retrieve, Upload).
    """
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all documents of the authenticated member",
        responses={200: serializers.MbrDocumentsSerializer()},
        tags=["Member"]
    )
    def get(self, request):
        """
        Get all documents for the authenticated member.
        """
        documents = models.MbrDocuments.objects.filter(card_number=request.user.mbrcardno).first()

        if not documents:
            return Response({"success": True, "data": {}}, status=status.HTTP_200_OK)

        serializer = serializers.MbrDocumentsSerializer(documents)
        data = dict(serializer.data)

        # Extract short resume file name if resume URL exists
        resume_url = documents.Resume
        if resume_url and resume_url.strip():
            path = urlparse(resume_url).path
            full_filename = os.path.basename(path)
            short_resume_name = full_filename[-15:] if len(full_filename) >= 15 else full_filename
            data["Resume_name"] = short_resume_name  # Add custom field

        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)

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
            
            # Prepare context for email
        context = {
            "full_name": full_name,
            "card_number": card_number,
            "view_url": "https://yourdomain.com/dashboard/documents",  # Replace with your actual dashboard link
            "logo_url": "https://yourdomain.com/static/jsjlogo-jobcard.png",  # Make sure the image is hosted correctly
        }

        # Send confirmation email using reusable template-based email function
        send_template_email(
            subject="✅ Document Upload Successful - JSJCard",
            template_name="email_template/upload_document.html",
            context=context,
            recipient_list=[email]
        )
        
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
        

class JobDetailAPIView(APIView):
    """
    API to retrieve detailed information about a specific job,
    and check if the member has uploaded a resume.
    """
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve job details by job ID and check resume status.",
        responses={200: JobpostSerializer()},
        tags=["Member"]
    )
    def get(self, request, job_id):
        try:
            member_card = request.user.mbrcardno

            # Get Job
            job = Job.objects.get(id=job_id)
            serializer = JobpostSerializer(job)

            # Check Resume
            is_resume = False
            resume_name = None
            try:
                doc = models.MbrDocuments.objects.get(card_number=member_card)
                resume_url = doc.Resume
                if resume_url and resume_url.strip():
                    is_resume = True
                    path = urlparse(resume_url).path
                    full_filename = os.path.basename(path)

                    # ✅ Get the last 15 characters of the filename
                    resume_name = full_filename[-15:] if len(full_filename) >= 15 else full_filename

            except models.MbrDocuments.DoesNotExist:
                pass

            return Response({
                "success": True,
                "message": "Job detail retrieved successfully.",
                "is_resume": is_resume,
                "resume": resume_name,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Job.DoesNotExist:
            return Response({
                "success": False,
                "message": "Job not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "success": False,
                "message": "Server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
    
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
            
            # Check resume status
            try:
                doc = models.MbrDocuments.objects.get(card_number=member_card)
                is_resume = bool(doc.Resume and doc.Resume.strip())
            except models.MbrDocuments.DoesNotExist:
                is_resume = False

            # Fetch applications
            applications = JobApplication.objects.filter(member_card=member_card).select_related('job').order_by('-applied_at')
            serializer = serializers.JobApplicationListSerializer(applications, many=True)

            return Response({
                "success": True,
                "message": "Applied jobs retrieved successfully.",
                "is_resume": is_resume,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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

                member_card = request.user.mbrcardno  # from SSO
                member_data = get_member_details_by_card(member_card)
                full_name = member_data.get('full_name')
                email = member_data.get('email')
                # Check if already applied
                if JobApplication.objects.filter(job=job, member_card=member_card).exists():
                    return Response({
                        "success": False,
                        "message": "You have already applied to this job."
                    }, status=status.HTTP_400_BAD_REQUEST)

                cover_letter = serializer.validated_data.get('cover_letter', '')
                institute_id = serializer.validated_data.get('institute_id') or None
                new_resume = serializer.validated_data.get('resume', '')

                # ✅ Check if Resume already exists in MbrDocuments
                doc_obj, created = models.MbrDocuments.objects.get_or_create(card_number=member_card)

                if doc_obj.Resume:  # If resume already exists
                    resume_to_use = doc_obj.Resume
                else:
                    resume_to_use = new_resume
                    doc_obj.Resume = resume_to_use  # Update resume
                    doc_obj.save()

                # ✅ Save Job Application with resume from documents table
                JobApplication.objects.create(
                    job=job,
                    member_card=member_card,
                    institute_id=institute_id,
                    cover_letter=cover_letter,
                    resume=resume_to_use
                )
                context = {
                   "full_name": full_name,
                    "mbrcardno": member_card,
                    "institute_id": institute_id or "N/A",
                    "resume": resume_to_use,
                    "cover_letter": cover_letter or "N/A"
                }
                send_template_email(
                    subject="Job Application Confirmation - JSJCard",
                    template_name="email_template/job_applied.html",
                    context=context,
                    recipient_list=[email] 
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

        
        

