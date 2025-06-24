from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from jobcard_business.models import Job, JobApplication
from . import serializers
from .authentication import SSOUserTokenAuthentication
from jobcard_member.models import MbrDocuments
from helpers.utils import get_member_details_by_card
import json
class ApplicationListOfStudent(APIView):
    """
    Staff can view job applications or update their status.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all student applications for a specific job ID.",
        responses={200: serializers.JobApplicationStaffViewSerializer(many=True)},
        tags=["Job Mitra"]
    )
    def get(self, request, job_id):
        try:
            applications = JobApplication.objects.filter(job_id=job_id)
            serializer = serializers.JobApplicationStaffViewSerializer(applications, many=True)
            return Response({
                "success": True,
                "message": "Applications retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
response_example = {
    "success": True,
    "is_resume": True,
    "resume": "hhgjhghjk",
    "data": {
        "full_name": "nitish kumar jha",
        "email": "mer1@jsj.com",
        "mobile_number": "7462982798",
        "first_name": "nitish",
        "last_name": "jha",
        "MbrCountryCode": "91",
        "MbrStatus": True,
        "card_purposes": [],
        "mbrcardno": 3109607606164910,
        "mbraddress": "bhubaneswar",
        "MbrPincode": "847301",
        "MbrReferalId": "",
        "MbrCreatedAt": "2025-06-03T12:15:19.203236Z",
        "MbrUpdatedAt": "2025-06-24T11:36:07.105820Z",
        "state": "Odisha",
        "district": "Khurda",
        "block": "Bhubaneswar",
        "village": "Patia",
        "pincode": "751024"
    }
}
class GetMemberDetailsByCardApi(APIView):
    """
    API to retrieve member details using card number,
    including resume status and resume value from MbrDocuments.
    """

    @swagger_auto_schema(
        operation_description="Enter member card number to retrieve member details and resume (if available).",
        manual_parameters=[
            openapi.Parameter(
                'card_number', openapi.IN_QUERY,
                description="Member card number",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Member data with resume",
                examples={
                    "application/json": response_example
                }
            ),
            404: openapi.Response(description="Member not found"),
            500: openapi.Response(description="Server error")
        },
        tags=["Job Mitra"]
    )
    def get(self, request):
        card_number = request.GET.get("card_number")
        if not card_number:
            return Response({
                "success": False,
                "message": "card_number query param is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 1: Get member info
            member_data = get_member_details_by_card(card_number)
            # print("✅ Raw member_data:", member_data)

            if not member_data:
                return Response({
                    "success": False,
                    "message": "Member not found or auth service unreachable."
                }, status=status.HTTP_404_NOT_FOUND)

            # Step 2: Fetch resume from MbrDocuments
            is_resume = False
            resume_value = None
            try:
                doc = MbrDocuments.objects.get(card_number=card_number)
                if doc.Resume and doc.Resume.strip():
                    is_resume = True
                    resume_value = doc.Resume
            except MbrDocuments.DoesNotExist:
                pass

            # Step 3: Extract meta_data (handling both dict and string cases)
            meta_data_raw = member_data.get("meta_data", {})
            # print("📦 meta_data raw:", meta_data_raw)
            # print("📦 meta_data type:", type(meta_data_raw))

            if isinstance(meta_data_raw, str):
                try:
                    meta_data = json.loads(meta_data_raw)
                except json.JSONDecodeError:
                    meta_data = {}
            else:
                meta_data = meta_data_raw or {}

            # print("✅ Parsed meta_data:", meta_data)

            # Step 4 & 5: Update member_data with address fields ONLY if present and non-empty in meta_data
            for field in ["state", "district", "block", "village", "pincode"]:
                value = meta_data.get(field)
                if value:  # update only if meta_data has non-empty value
                    member_data[field] = value

            # print("🏠 Final address fields in member_data:", {f: member_data.get(f) for f in ["state", "district", "block", "village", "pincode"]})

            # Step 6: Return response
            return Response({
                "success": True,
                "is_resume": is_resume,
                "resume": resume_value,
                "data": member_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("🔥 Exception occurred:", str(e))
            return Response({
                "success": False,
                "message": "Internal server error.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







class ApplyJobForMemberAPIView(APIView):
    """
    job mitra applies for a job on behalf of a member using their card number.
    """

    @swagger_auto_schema(
        operation_description="Apply for a job using member card number.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["card_number", "job_id", "resume"],
            properties={
                "card_number": openapi.Schema(type=openapi.TYPE_STRING, description="Member's card number"),
                "job_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Job ID to apply for"),
                "resume": openapi.Schema(type=openapi.TYPE_STRING, description="Resume file/link"),
                "cover_letter": openapi.Schema(type=openapi.TYPE_STRING, description="Optional cover letter", default=""),
                "institute_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Optional institute ID", default=None),
            }
        ),
        responses={
            201: openapi.Response(description="Job application created."),
            400: openapi.Response(description="Invalid request or already applied."),
            404: openapi.Response(description="Member or Job not found.")
        },
        tags=["Job Mitra"]
    )
    def post(self, request):
        card_number = request.data.get('card_number')
        job_id = request.data.get('job_id')
        resume = request.data.get('resume')
        cover_letter = request.data.get('cover_letter', "")
        institute_id = request.data.get('institute_id', None)

        # Step 1: Validate card number and member
        member_data = get_member_details_by_card(card_number)
        if not member_data:
            return Response({"success": False, "message": "Invalid card number or member not found."}, status=404)

        # Step 2: Check Job existence
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"success": False, "message": "Invalid job ID."}, status=404)

        # Step 3: Check if already applied
        if JobApplication.objects.filter(job=job, member_card=card_number).exists():
            return Response({
                "success": False,
                "message": "Member has already applied to this job."
            }, status=400)

        # Step 4: Check if resume exists in MbrDocuments or use given resume
        try:
            doc = MbrDocuments.objects.get(card_number=card_number)
            has_resume = bool(doc.Resume and doc.Resume.strip())
        except MbrDocuments.DoesNotExist:
            has_resume = False

        if not resume and not has_resume:
            return Response({
                "success": False,
                "message": "Resume is required either via request or in MbrDocuments."
            }, status=400)
            
        # Get referral (employee id) from the logged-in user
        referral_id = getattr(request.user, 'employee_id', None)

        # Step 5: Create application
        JobApplication.objects.create(
            job=job,
            member_card=card_number,
            institute_id=institute_id,
            cover_letter=cover_letter,
            resume=resume or doc.Resume,
            referral=referral_id
        )

        return Response({
            "success": True,
            "message": "Job application submitted successfully for member.",
            "member_name": member_data.get("full_name"),
            "job_title": job.title
        }, status=201)