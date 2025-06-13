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
from jobcard_staff.models import JobApplication
from .serializers import JobApplicationSerializer




class MbrDocumentsAPI(APIView):
    """
    API to handle Member Documents (Retrieve, Upload).
    """
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all documents of the authenticated member",
        responses={200: serializers.MbrDocumentsSerializer()}
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
        responses={200: serializers.MbrDocumentsSerializer()}
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
    
class JobApplicationCreateView(generics.CreateAPIView):
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    serializer_class = JobApplicationSerializer
    queryset = JobApplication.objects.all()

    @swagger_auto_schema(
        operation_summary="Student Apply for a Job",
        operation_description="Allows an authenticated student to apply for a job with resume upload.",
        manual_parameters=[],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["job", "candidate_name", "candidate_email", "location", "resume"],
            properties={
                'job': openapi.Schema(type=openapi.TYPE_INTEGER, description="Job ID"),
                'candidate_name': openapi.Schema(type=openapi.TYPE_STRING),
                'candidate_email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'cover_letter': openapi.Schema(type=openapi.TYPE_STRING),
                'resume': openapi.Schema(type=openapi.TYPE_FILE),
            }
        )
    )
    def post(self, request):
        """
        Submit a job application for the authenticated student.
        Automatically assigns member_id from request.user.
        """
        member_id = request.user.mbrcardno  # Get member ID from the logged-in student
        data = request.data.copy()
        data['member_id'] = member_id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Job application submitted successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)