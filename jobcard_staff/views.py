from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from jobcard_business.models import Job, JobApplication, HRFeedback
from . import serializers
from .authentication import SSOUserTokenAuthentication
from jobcard_member.models import MbrDocuments, DocumentVerificationRequest
from jobcard_member.serializers import MbrDocumentsSerializer
from helpers.utils import get_business_details_by_id, get_member_details_by_card
from helpers.pagination import paginate
from helpers.email import send_template_email
class JobListCreateAPIView(APIView):
    """
    API to list all jobs or create a new job post.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a paginated list of all job postings.",
        responses={200: serializers.JobpostSerializer(many=True)},
        tags=["Staff"]
    )
    def get(self, request):
        try:
            if request.user.is_jobmitra:
                for job in Job.objects.filter(is_active=True):
                    job.check_and_deactivate()
                jobs = Job.objects.filter(is_active=True).order_by("-id")  # order by latest
            else:
                jobs = Job.objects.all().order_by('-id')
            # Use paginate helper
            page, pagination_meta = paginate(
                request,
                jobs,
                data_per_page=int(request.GET.get("page_size", 10))
            )

            serializer = serializers.JobpostSerializer(page, many=True)

            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": serializer.data,
                "pagination_meta_data": pagination_meta
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new job post.",
        request_body=serializers.JobpostSerializer,
        responses={201: serializers.JobpostSerializer},tags=["Staff"]
    )
    def post(self, request):
        try:
            serializer = serializers.JobpostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Job created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "success": False,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobDetailAPIView(APIView):
    """
    API to retrieve, update, or delete a job post by ID.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a job by its ID.",
        responses={200: serializers.JobpostSerializer()},tags=["Staff"]
    )
    def get(self, request, id):
        try:
            job = Job.objects.get(id=id)
            serializer = serializers.JobpostSerializer(job)
            return Response({
                "success": True,
                "message": "Job retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_description="Update a job post by its ID.",
        request_body=serializers.JobpostSerializer,
        responses={200: serializers.JobpostSerializer()},
        tags=["Staff"]
    )
    def put(self, request, id):
        try:
            job = Job.objects.get(id=id)
            serializer = serializers.JobpostSerializer(job, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Job updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            return Response({"success": False, "message": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        

class JobApplicationListOfStudent(APIView):
    """
    Staff can view job applications or update their status.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all student applications for a specific job ID.",
        responses={200: serializers.JobApplicationStaffViewSerializer(many=True)},
        tags=["Staff"]
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
    @swagger_auto_schema(
        operation_description="Update status of a job application (by application ID).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id", "status"],
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the application"),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New status (applied, under_review, shortlisted, rejected, selected)",
                    enum=["applied", "under_review", "shortlisted", "rejected", "selected"]
                )
            }
        ),
        responses={
            200: openapi.Response(description="Application status updated"),
            404: openapi.Response(description="Application not found"),
            400: openapi.Response(description="Invalid input")
        },
        tags=["Staff"]
    )
    def patch(self, request, job_id):
        application_id = request.data.get("id")
        new_status = request.data.get("status")

        if not application_id or not new_status:
            return Response({
                "success": False,
                "message": "application_id and status are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            application = JobApplication.objects.get(id=application_id, job_id=job_id)
            application.status = new_status
            application.save()
            
            member_data = get_member_details_by_card(application.member_card)
            email = member_data.get("email")
            full_name = member_data.get("full_name")

            # Prepare email context
            context = {
                "applicant_name": full_name,
                "job_title": application.job.title,   # adjust if job has another field
                "status": new_status,
                "company_name": application.job.company_name,
                "card_number": application.member_card,           # optional, if you want to show in email
            }

            # Send email to applicant
            send_template_email(
                subject="Job Application Status Update - JSJCard",
                template_name="email_template/job_status.html",
                context=context,
                recipient_list=[email]  # sending to member email
            )


            return Response({
                "success": True,
                "message": "Application status updated successfully.",
                "application_id": application.id,
                "new_status": application.status
            }, status=status.HTTP_200_OK)

        except JobApplication.DoesNotExist:
            return Response({
                "success": False,
                "message": "Application not found for the given job."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
            
class MbrDocumentsAPI(APIView):
    """
    Staff can view documents submitted by candidates.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all candidate documents filtered by member card number.",
        manual_parameters=[
            openapi.Parameter(
                'card_number',
                openapi.IN_PATH,
                description="Candidate's member card number",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: openapi.Response(
            description="List of submitted documents",
            schema=MbrDocumentsSerializer(many=True)
        )},
        tags=["Staff"]
    )
    def get(self, request, card_number):
        try:
           
            documents = MbrDocuments.objects.filter(card_number=card_number)
            

            serializer = MbrDocumentsSerializer(documents, many=True)

            return Response({
                "success": True,
                "message": "Documents retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while retrieving documents.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            







class StaffDocumentVerificationListAPIView(APIView):
    """
    View all requested document verifications (paginated).
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = DocumentVerificationRequest.objects.all().order_by('-created_at')

        # Use your custom paginate function
        page, pagination_meta = paginate(
            request,
            requests,
            data_per_page=int(request.GET.get("page_size", 10))
        )

        data = []
        for r in page:
            request_by = get_business_details_by_id(r.requested_by)
            business_name = request_by.get('business_name', 'Unknown') if request_by else 'Unknown'

            data.append({
                "request_id": r.id,
                "card_number": r.card_number,
                "documents": r.documents,  # JSON of requested documents
                "status": r.status,
                "requested_by": business_name,
                "requested_at": r.created_at,
            })

        return Response({
            "status": 200,
            "message": "Document verification requests fetched successfully.",
            "data": data,
            "pagination_meta_data": pagination_meta
        }, status=status.HTTP_200_OK)





class StaffUpdateDocumentStatusAPIView(APIView):
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, card_number):
        """
        View all requested document verifications + return requested files with their status.
        """
        try:
            mbr_docs = MbrDocuments.objects.get(card_number=card_number)
            mbr_docs_data = MbrDocumentsSerializer(mbr_docs).data
            doc_status_data = mbr_docs_data.get("document_status", {}) or {}
        except MbrDocuments.DoesNotExist:
            return Response({
                "success": False,
                "message": "Member documents not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Fetch verification requests
        requests = DocumentVerificationRequest.objects.filter(card_number=card_number)
        if not requests.exists():
            return Response({
                "success": False,
                "message": "No verification requests found."
            }, status=status.HTTP_404_NOT_FOUND)

        response_data = []
        for req in requests:
            requested_docs = req.documents or {}  # dict of requested docs

            documents_info = {}
            for doc_name in requested_docs.keys():
                documents_info[doc_name] = {
                    "file": mbr_docs_data.get(doc_name, ""),
                    "status": doc_status_data.get(doc_name, "pending")
                }

            response_data.append({
                "id": req.id,
                "status": req.status,
                "documents": documents_info
            })

        return Response({
            "success": True,
            "message": "Document verification requests fetched.",
            "data": response_data,
        }, status=status.HTTP_200_OK)


    def post(self, request, card_number):
        """Update the status of an individual document"""
        request_id = request.data.get("request_id")
        document_name = request.data.get("document_name")
        status_value = request.data.get("status")  # "verified" or "rejected"

        if not request_id or not document_name or not status_value:
            return Response({"success": False, "message": "All fields are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            doc_request = DocumentVerificationRequest.objects.get(id=request_id, card_number=card_number)
        except DocumentVerificationRequest.DoesNotExist:
            return Response({"success": False, "message": "Request not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # Update the document status
        doc_request.documents[document_name] = status_value
        doc_request.save(update_fields=["documents", "updated_at"])

        # Also update the main MbrDocuments table
        mbr_docs = MbrDocuments.objects.get(card_number=doc_request.card_number)
        doc_status = mbr_docs.document_status or {}
        doc_status[document_name] = status_value
        mbr_docs.document_status = doc_status
        mbr_docs.save(update_fields=["document_status", "UpdatedAt"])

        return Response({
            "success": True,
            "message": f"{document_name} updated to {status_value}",
            "document_status": doc_status
        }, status=status.HTTP_200_OK)


class HRFeedbackListAPI(APIView):
    """
    API for staff to view all HR feedbacks.
    Each record contains candidate details and multiple company feedbacks.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get list of all HR Feedback records (for staff use).",
        responses={200: "List of all candidate feedbacks"},
        tags=["HR Feedback"]
    )
    def get(self, request):
        try:
            feedbacks = HRFeedback.objects.all().values(
                "id", "candidate_name", "card_number", "feedbacks", "created_at", "updated_at"
            )

            if not feedbacks:
                return Response({
                    "success": False,
                    "message": "No feedback records found."
                }, status=404)

            return Response({
                "success": True,
                "count": feedbacks.count(),
                "data": list(feedbacks)
            }, status=200)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Something went wrong: {str(e)}"
            }, status=500)