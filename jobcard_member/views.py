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
from jobcard_business.models import JobApplication, Job, Feedback
from jobcard_staff.serializers import JobpostSerializer
import os
from urllib.parse import urlparse
import re
from helpers.email import send_template_email
from django.utils import timezone
from datetime import timedelta

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
    responses={200: serializers.MbrDocumentsSerializer()},
    tags=["Member"]
    )
    def post(self, request):
        """
        Upload or update document URLs for the authenticated member.
        Existing documents are preserved if not included in the request.
        Only actual documents are tracked in document_status.
        """
        card_number = request.user.mbrcardno

        # Get or create the document instance for this card number
        documents, created = models.MbrDocuments.objects.get_or_create(card_number=card_number)

        # Convert existing data to dict
        existing_data = serializers.MbrDocumentsSerializer(documents).data

        # Initialize or copy existing document_status
        document_status = documents.document_status or {}

        # Define actual document fields to track
        document_fields = [
            "TenthCertificate",
            "TwelfthCertificate",
            "GraduationCertificate",
            "GraduationMarksheet",
            "PgCertificate",
            "UpskillCertificate",
            "ItiCertificate",
            "ItiMarksheet",
            "DiplomaCertificate",
            "DiplomaMarksheet",
            "CoverLetter",
            "Resume"
        ]

        merged_data = {}
        for field in document_fields:
            if field in request.data and request.data[field] not in [None, ""]:
                merged_data[field] = request.data[field]
                document_status[field] = "pending"  # new upload → pending
            else:
                merged_data[field] = existing_data.get(field)
                if field not in document_status:
                    document_status[field] = "pending"

        # Include updated document_status in merged_data
        merged_data["document_status"] = document_status

        # Save updated data
        serializer = serializers.MbrDocumentsSerializer(documents, data=merged_data, partial=True)
        if serializer.is_valid():
            serializer.save(card_number=card_number)
            return Response({
                "success": True,
                "message": "Documents updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    
    
class JoblistAPIView(APIView):
    """
    API for a member list of job with their application status.
    """
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings with the current member's application status.",
        responses={200: JobpostSerializer(many=True)},
        tags=["Member"]
    )
    def get(self, request):
        try:
            member_card = request.user.mbrcardno
            jobs = Job.objects.all().order_by('-created_at')
            job_list = []

            for job in jobs:
                # Check if member has applied to this job
                application = JobApplication.objects.filter(job=job, member_card=member_card).first()
                job_data = JobpostSerializer(job).data
                job_data['status'] = application.status if application else None
                job_list.append(job_data)

            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": job_list
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

        
        

class ShareDocumentsAPIView(APIView):
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Share selected documents of a member using card number. Access will be protected with a PIN and expire after the specified time in minutes.",
        request_body=serializers.DocumentShareSerializer,
        responses={200: "Document access created"},
        tags=["Member"]
    )
    def post(self, request):
        serializer = serializers.DocumentShareSerializer(data=request.data)
        
        if serializer.is_valid():
            card_number = request.user.mbrcardno
            selected_fields = serializer.validated_data["selected_fields"]
            pin = serializer.validated_data["pin"]
            minutes = serializer.validated_data["access_time_minutes"]

            try:
                member = models.MbrDocuments.objects.get(card_number=card_number)
            except models.MbrDocuments.DoesNotExist:
                return Response({"error": "Member not found."}, status=404)

            access = models.DocumentAccess.objects.create(
                member=member,
                selected_fields=selected_fields,
                pin=pin,
                expiry_time=timezone.now() + timedelta(minutes=minutes)
            )
            return Response({"message": "Document access created", "access_id": access.id})
        return Response(serializer.errors, status=400)
    
    
    
    
    
class ViewSharedDocumentsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="View shared documents by providing access ID and PIN. Access is only valid for a limited time.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["access_id", "pin"],
            properties={
                "access_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "pin": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: "Documents retrieved successfully", 403: "Access expired", 404: "Invalid access ID or PIN"},
        tags=["Member"]
    )
    def post(self, request):
        access_id = request.data.get("access_id")
        pin = request.data.get("pin")

        try:
            access = models.DocumentAccess.objects.get(id=access_id, pin=pin)
        except models.DocumentAccess.DoesNotExist:
            return Response({"error": "Invalid access ID or PIN"}, status=404)

        if not access.is_valid():
            return Response({"error": "Access expired"}, status=403)

        member = access.member
        data = {field: getattr(member, field) for field in access.selected_fields}
        return Response({"documents": data})



class FeedbackView(APIView):
    """
    Submit feedback or view feedback by card number
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SSOMemberTokenAuthentication]

    @swagger_auto_schema(
        operation_summary="Get feedback by user card number and business ID",
        manual_parameters=[
            openapi.Parameter(
                'businessId',
                openapi.IN_QUERY,
                description="Business ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: serializers.FeedbackSerializer(many=True)}
    )
    def get(self, request):
        business_id = request.query_params.get("businessId")
        card_number = request.user.mbrcardno
        member_data = get_member_details_by_card(card_number)
        full_name = member_data.get('full_name')
        mobile_number = member_data.get('mobile_number')
        if not business_id:
            return Response({"error": "businessId query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        feedbacks = Feedback.objects.filter(card_number=card_number, business_id=business_id).order_by('-created_at')
        serializer = serializers.FeedbackSerializer(feedbacks, many=True)

        return Response({
            "full_name": full_name,
            "mobile_number": mobile_number,
            "business_id": business_id,
            "feedbacks": serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Submit Feedback",
        request_body=serializers.FeedbackSerializer,
        responses={201: serializers.FeedbackSerializer}
    )
    def post(self, request):
        business_id = request.query_params.get("businessId")
        card_number = request.user.mbrcardno

        if not business_id or not card_number:
            return Response({"error": "Missing businessId or card_number"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['business_id'] = business_id
        data['card_number'] = card_number

        serializer = serializers.FeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Feedback submitted successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    



