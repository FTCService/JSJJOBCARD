from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from jobcard_business.models import Job
#from jobcard_member.models import Member
from jobcard_staff.serializers import JobpostSerializer, JobMitraApplySerializer
from jobcard_member.serializers import JobApplicationListSerializer
from django.utils import timezone
from .authentication import SSOUserTokenAuthentication
import traceback


class JobMitraJobListView(APIView):
    """
    API to list active jobs filtered by Job Mitra location.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve job posts assigned to a Job Mitra location or global jobs.",
        responses={200: JobpostSerializer(many=True)},
        tags=["Job Mitra"]
    )
    def get(self, request, location):  # ✅ location in path
        try:
            jobs = Job.objects.filter(
                is_active=True
            ).filter(
                Q(job_mitra_location__iexact=location) |
                Q(job_mitra_location__isnull=True) |
                Q(job_mitra_location__exact="")
            )

            serializer = JobpostSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": f"Jobs for location '{location}' retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({
                "success": False,
                "message": f"Internal Server Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
class JobMitraApplicationListAPIView(APIView):
    """
    Job Mitra API to view applications submitted on behalf of candidates.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Job Mitra - View Candidate Applications",
        manual_parameters=[
            openapi.Parameter('job_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by Job ID", required=False),
            openapi.Parameter('member_card', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by Member Card", required=False),
        ],
        responses={200: JobApplicationListSerializer(many=True)},
        tags=["Job Mitra"]
    )
    def get(self, request):
        job_id = request.query_params.get("job_id")
        member_card = request.query_params.get("member_card")

        applications = JobApplication.objects.all()

        if job_id:
            applications = applications.filter(job_id=job_id)
        if member_card:
            applications = applications.filter(member_card=member_card)

        serializer = JobApplicationListSerializer(applications, many=True)
        return Response({
            "success": True,
            "message": "Applications retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
class JobMitraApplyAPIView(APIView):
    """
    Job Mitra applies to a job using only the member card number and adds resume.
    """

    @swagger_auto_schema(
        operation_description="Apply to a job on behalf of a member using their member card number and resume.",
        request_body=JobMitraApplySerializer,
        tags=["Job Mitra"],
        responses={
            201: openapi.Response(
                description="Application successful",
                examples={"application/json": {"success": True, "message": "Applied successfully"}}
            ),
            400: openapi.Response(
                description="Already applied or bad request",
                examples={"application/json": {"success": False, "message": "Already applied to this job."}}
            ),
            404: openapi.Response(
                description="Member or Job not found",
                examples={"application/json": {"success": False, "message": "Member not found."}}
            )
        }
    )
    def post(self, request, job_id):
        serializer = JobMitraApplySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        member_card = serializer.validated_data.get("member_card")
        resume = serializer.validated_data.get("resume")
        cover_letter = serializer.validated_data.get("cover_letter", "")

        # ✅ Get Member
        try:
            member = Member.objects.get(mbrcardno=member_card)
        except Member.DoesNotExist:
            return Response({
                "success": False,
                "message": "Member not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Get Job
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({
                "success": False,
                "message": "Job not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check Duplicate
        if JobApplication.objects.filter(job=job, member_card=member_card).exists():
            return Response({
                "success": False,
                "message": "Already applied to this job."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Create Application
        try:
            JobApplication.objects.create(
                job=job,
                member_card=member_card,
                resume=resume,
                cover_letter=cover_letter,
                applied_at=timezone.now(),
                status="applied"
            )

            return Response({
                "success": True,
                "message": "Applied successfully"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            return Response({
                "success": False,
                "message": f"Internal Server Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)