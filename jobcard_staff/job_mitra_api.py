from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from jobcard_business.models import Job, JobApplication
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
    Job Mitra API to comment on candidate profiles by job ID and view submitted applications.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Job Mitra - Comment on Candidate Profile",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['job_id', 'member_card', 'comment'],
            properties={
                'job_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Job ID'),
                'member_card': openapi.Schema(type=openapi.TYPE_INTEGER, description='Member card number of the candidate'),
                'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Comment by Job Mitra'),
            },
        ),
        responses={
            200: "Comment added successfully",
            400: "Bad Request",
            404: "Application not found"
        },
        tags=["Job Mitra"]
    )
    def post(self, request):  # ✅ Line 80
        job_id = request.data.get("job_id")  # ✅ Must be indented
        member_card = request.data.get("member_card")
        comment = request.data.get("comment")

        if not job_id or not member_card or comment is None:
            return Response({
                "success": False,
                "message": "'job_id', 'member_card', and 'comment' are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            application = JobApplication.objects.get(job_id=job_id, member_card=member_card)
            application.jobmitra_comment = comment
            application.save()

            return Response({
                "success": True,
                "message": f"Comment added to application of member {member_card} for job {job_id}."
            }, status=status.HTTP_200_OK)

        except JobApplication.DoesNotExist:
            return Response({
                "success": False,
                "message": "Application not found for the given job and member card."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({
                "success": False,
                "message": f"Internal Server Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    Job Mitra applies to a job using only the member card number.
    """

    @swagger_auto_schema(
        operation_description="Apply to a job using only member card number.",
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
                description="Job not found",
                examples={"application/json": {"success": False, "message": "Job not found."}}
            )
        }
    )
    def post(self, request, job_id):
        serializer = JobMitraApplySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        member_card = serializer.validated_data.get("member_card")

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

