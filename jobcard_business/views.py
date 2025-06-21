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
from jobcard_member.serializers import MbrDocumentsSerializer
from jobcard_business import models

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
        
        
class MbrDocumentsByCardAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="HR Management: Get Member Documents",
        operation_description="Retrieve documents for a member by card number",
        manual_parameters=[
            openapi.Parameter(
                name='card_number',
                in_=openapi.IN_PATH,
                description="Member's Card Number",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: MbrDocumentsSerializer,
            404: "Member not found"
        },
        tags=["HR Management"]
    )
    def get(self, request, card_number):
        doc = MbrDocuments.objects.filter(card_number=card_number).first()
        if not doc:
            return Response({"success": False, "message": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MbrDocumentsSerializer(doc)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)