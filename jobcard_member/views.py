import uuid
import boto3
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from .authentication import SSOMemberTokenAuthentication

from .models import Document
from .serializers import DocumentSerializer


class Documentapi(APIView):
    authentication_classes = [SSOMemberTokenAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get all documents uploaded by the authenticated member",
        responses={200: DocumentSerializer(many=True)}
    )
    def get(self, request):
        member_id = request.user.mbrcardno
        documents = Document.objects.filter(member=member_id)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @swagger_auto_schema(
        operation_description="Upload multiple documents and save URLs in database (direct upload to S3).",
        request_body=DocumentSerializer,
        responses={201: DocumentSerializer, 400: 'Validation error'}
    )
    def post(self, request):
        file_fields = [
            'tenth_certificate',
            'twelfth_certificate',
            'graduation_certificate',
            'pg_certificate',
            'graduation_marksheet',
            'technical_certification',
            'language_certification',
            'soft_skill_certification',
            'aadhaar_card',
            'pan_card',
            'passport',
            'driving_license',
            'resume',
            'offer_letter',
            'personal_statement',
        ]
        member = request.user.mbrcardno
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        uploaded_data = {}

        for field in file_fields:
            uploaded_file = request.FILES.get(field)
            if not uploaded_file:
                continue

            unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            s3_key = f"documents/{unique_filename}"

            try:
                s3_client.upload_fileobj(
                    Fileobj=uploaded_file,
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=s3_key,
                    ExtraArgs={'ContentType': uploaded_file.content_type}
                )
                s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
                uploaded_data[field] = s3_url

            except Exception as e:
                return Response({'error': f"Upload failed for {field}: {str(e)}"}, status=500)

        if not uploaded_data:
            return Response({'error': 'No files uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.create(member=member, **uploaded_data)
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    
