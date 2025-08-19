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
from jobcard_business import models, serializers
from jobcard_member.serializers import MbrDocumentsSerializer
from jobcard_member.models import MbrDocuments, DocumentVerificationRequest
from helpers.utils import get_member_details_by_mobile, get_member_details_by_card, get_business_details_by_id

class JobListBusinessAPIView(APIView):
    """
    API to list all jobs or create a new job post.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings.",
        responses={200: JobpostSerializer(many=True)},
        tags=["Business"]
    )
    def get(self, request):
        try:
            business = request.user.business_id
            print(f"Authenticated Business ID: {business}")

            if not business:
                return Response({
                    "success": False,
                    "message": "Authenticated user is not associated with a business."
                }, status=status.HTTP_400_BAD_REQUEST)

            jobs = models.Job.objects.filter(business_id=business).order_by('-created_at')
            serializer = JobpostSerializer(jobs, many=True)

            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=JobpostSerializer,
        operation_description="Create a new job post.",
        responses={201: JobpostSerializer()},
        tags=["Business"]
    )
    def post(self, request):
        try:
            business = request.user.business_id
            print(f"Posting Job for Business ID: {business}")

            if not business:
                return Response({
                    "success": False,
                    "message": "Authenticated user is not associated with a business."
                }, status=status.HTTP_400_BAD_REQUEST)

            data = request.data.copy()
            data['business_id'] = business  # Make sure field name matches model

            serializer = JobpostSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Job post created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            # Log serializer errors to console
            print("Serializer Errors:", serializer.errors)

            return Response({
                "success": False,
                "message": "Invalid data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                
                
            
            

class JobDetailBusinessAPIView(APIView):
    """
    API to retrieve, update, or delete a job post by ID.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a job by its ID.",
        responses={200: JobpostSerializer()},tags=["Business"]
    )
    def get(self, request, job_id):
        try:
            job = models.Job.objects.get(id=job_id)
            serializer = JobpostSerializer(job)
            return Response({
                "success": True,
                "message": "Job retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobApplicationListBusinessAPI(APIView):
    """
    API to list all applications for jobs posted by the authenticated business.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all job applications received for this business.",
        responses={200: serializers.JobApplicationListForBusinessSerializer(many=True)},tags=["Business"]
    )
    def get(self, request, job_id):
        try:
            # business_id = request.user.business_id
            # if not business_id:
            #     return Response({
            #         "success": False,
            #         "message": "Authenticated user is not associated with a business."
            #     }, status=status.HTTP_400_BAD_REQUEST)
           
            applications = models.JobApplication.objects.filter(job_id=job_id)
            serializer = serializers.JobApplicationListForBusinessSerializer(applications, many=True)

            return Response({
                "success": True,
                "message": "Job applications retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
class EmployerDashboardAPIView(APIView):
    """
    API for employer dashboard summary:
    - Total jobs posted
    - Total applications received
    - Total students placed
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get employer dashboard stats: total jobs, applications, and placed students.",
        responses={200: 'Dashboard Stats'},
        tags=["Business"]
    )
    def get(self, request):
        try:
            business_id = request.user.business_id
            if not business_id:
                return Response({
                    "success": False,
                    "message": "Authenticated user is not associated with a business."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get all jobs for this business
            job_ids = models.Job.objects.filter(business_id=business_id).values_list('id', flat=True)

            # Total jobs
            total_jobs = job_ids.count()

            # Total applications across all jobs
            total_applications = models.JobApplication.objects.filter(job_id__in=job_ids).count()

            # Total placed students (assuming status = 'placed' or 'selected')
            total_placed = models.JobApplication.objects.filter(
                job_id__in=job_ids,
                status__in=["placed", "selected"]
            ).count()

            return Response({
                "success": True,
                "message": "Dashboard data retrieved successfully.",
                "data": {
                    "total_jobs": total_jobs,
                    "total_applications": total_applications,
                    "total_placed_students": total_placed
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "Server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetMemberDocumentsAPIView(APIView):
    """
    API to fetch documents for a member by card number or mobile number.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: MbrDocumentsSerializer()},
        tags=["Job Profile Management"]
    )
    def get(self, request, card_number):
        card_no = str(card_number).strip()

        # ✅ Decide whether it's a card number or mobile number
        mbrcardno = None
        full_name = None 
        if len(card_no) == 16 and card_no.isdigit():
            # Directly use as card number
            mbrcardno = card_no
        elif len(card_no) == 10 and card_no.isdigit():
            # Lookup by mobile number
            member_data = get_member_details_by_mobile(card_no)
            mbrcardno = member_data.get("mbrcardno") if member_data else None
            full_name = member_data.get("full_name") if member_data else None
        else:
            return Response(
                {"error": "Invalid input. Provide a valid 16-digit card number or 10-digit mobile number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not mbrcardno:
            return Response(
                {"success": False, "message": "Member not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Fetch documents
        try:
            documents = MbrDocuments.objects.get(card_number=mbrcardno)
            serializer = MbrDocumentsSerializer(documents)
            return Response({
                "success": True,
                "message": "Documents fetched successfully.",
                "full_name": full_name,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except MbrDocuments.DoesNotExist:
            return Response(
                {"success": False, "message": "Documents not found for this member."},
                status=status.HTTP_404_NOT_FOUND
            )
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "documents": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Documents to request verification for, e.g. {'Resume': 'pending', 'TenthCertificate': 'pending'}"
                ),
            },
            required=["documents"]
        ),
        responses={201: "Document verification request created"},
        tags=["Document Management"]
    )
    def post(self, request, card_number):
        """HR can create a document verification request for a staff member"""
        documents = request.data.get("documents")
        requested_by = request.user.business_id  # HR user ID

        if not card_number or not documents:
            return Response({"success": False, "message": "card_number and documents are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create the verification request
        doc_request = DocumentVerificationRequest.objects.create(
            card_number=card_number,
            requested_by=requested_by,
            documents=documents
        )

        return Response({
            "success": True,
            "message": "Document verification request created successfully",
            "data": {
                "id": doc_request.id,
                "card_number": doc_request.card_number,
                "documents": doc_request.documents,
                "status": doc_request.status
            }
        }, status=status.HTTP_201_CREATED)
