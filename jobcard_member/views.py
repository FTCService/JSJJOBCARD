from django.conf import settings
from rest_framework.views import APIView
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
