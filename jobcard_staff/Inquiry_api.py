from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import Inquiry
from .serializers import InquirySerializer

class InquiryListCreateAPI(APIView):
    """
    List all inquiries or create a new one.
    """

    @swagger_auto_schema(
        operation_description="List all submitted inquiries.",
        responses={200: InquirySerializer(many=True)},
        tags=["Inquiry"]
    )
    def get(self, request):
        inquiries = Inquiry.objects.all()
        serializer = InquirySerializer(inquiries, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new inquiry.",
        request_body=InquirySerializer,
        responses={201: InquirySerializer},
        tags=["Inquiry"]
    )
    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Inquiry created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
