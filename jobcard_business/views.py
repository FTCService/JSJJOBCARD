from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Job, Document
from .serializers import JobSerializer, DocumentSerializer
from .authentication import SSOBusinessTokenAuthentication

class DocumentByCardNumber(APIView):
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get documents uploaded by a specific member using their card number",
        manual_parameters=[
            openapi.Parameter(
                'card_number', openapi.IN_QUERY, description="Member card number", type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={200: DocumentSerializer(many=True)}
    )
    def get(self, request):
        card_number = request.query_params.get('card_number')

        if not card_number:
            return Response({'error': 'card_number parameter is required'}, status=400)

        documents = Document.objects.filter(member=card_number)
        if not documents.exists():
            return Response({'message': 'No documents found for this card number'}, status=404)

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class JobListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings. You can filter by job_type, location, and industry.",
        manual_parameters=[
            openapi.Parameter(
                'job_type',
                openapi.IN_QUERY,
                description="Filter by job type (e.g. Full Time, Part Time)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'location',
                openapi.IN_QUERY,
                description="Filter by job location",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'industry',
                openapi.IN_QUERY,
                description="Filter by industry",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={200: JobSerializer(many=True)}
    )
    def get(self, request):
        jobs = Job.objects.all().order_by('-created_at')

        job_type = request.query_params.get('job_type')
        location = request.query_params.get('location')
        industry = request.query_params.get('industry')

        if job_type:
            jobs = jobs.filter(job_type=job_type)
        if location:
            jobs = jobs.filter(location__icontains=location)
        if industry:
            jobs = jobs.filter(industry__icontains=industry)

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobPostView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=JobSerializer,
        operation_description="Create a new job post",
        responses={201: JobSerializer()}
    )
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
