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

        mbrcardno = None
        full_name = None 
        if len(card_number) == 16 and card_number.isdigit():
            # Directly use as card number
            mbrcardno = card_number
        elif len(card_number) == 10 and card_number.isdigit():
            # Lookup by mobile number
            member_data = get_member_details_by_mobile(card_number)
            mbrcardno = member_data.get("mbrcardno") if member_data else None
           
        else:
            return Response({"success": False, "message": " documents are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create the verification request
        doc_request = DocumentVerificationRequest.objects.create(
            card_number=mbrcardno,
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


class HRFeedbackCreateAPIView(APIView):
    """
    HR can add a feedback for a candidate.
    Supports multiple company feedbacks for a single card_number.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'card_or_mobile', openapi.IN_PATH,
                description="16-digit card number or 10-digit mobile number",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["candidate_name", "company_name"],
            properties={
                "candidate_name": openapi.Schema(type=openapi.TYPE_STRING, description="Candidate full name"),
                "company_name": openapi.Schema(type=openapi.TYPE_STRING, description="Company name"),
                "job_title": openapi.Schema(type=openapi.TYPE_STRING, description="Job title"),
                "employee_id": openapi.Schema(type=openapi.TYPE_STRING, description="Employee ID"),
                "feedback_questions": openapi.Schema(type=openapi.TYPE_OBJECT, description="JSON of questions and answers"),
                "comments": openapi.Schema(type=openapi.TYPE_STRING, description="Additional comments")
            }
        ),
        responses={201: serializers.HRFeedbackSerializer()},
        tags=["HR Feedback"]
    )
    def post(self, request, card_or_mobile):
        card_or_mobile = str(card_or_mobile).strip()
        card_number = None

        # Determine if it's card number or mobile number
        if len(card_or_mobile) == 16 and card_or_mobile.isdigit():
            card_number = card_or_mobile
        elif len(card_or_mobile) == 10 and card_or_mobile.isdigit():
            member_data = get_member_details_by_mobile(card_or_mobile)
            if member_data:
                card_number = member_data.get("mbrcardno")
            else:
                return Response({"success": False, "message": "Member not found for this mobile number."},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"success": False, "message": "Invalid card number or mobile number."},
                            status=status.HTTP_400_BAD_REQUEST)

        candidate_name = request.data.get("candidate_name")
        new_feedback = {
            "company_name": request.data.get("company_name"),
            "job_title": request.data.get("job_title"),
            "employee_id": request.data.get("employee_id"),
            "feedback_questions": request.data.get("feedback_questions"),
            "comments": request.data.get("comments"),
            "business_id": request.user.business_id  # HR submitting the feedback
        }

        if not card_number or not candidate_name or not new_feedback["company_name"]:
            return Response({"success": False, "message": "card_number, candidate_name, and company_name are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get or create feedback object
        feedback_obj, created = models.HRFeedback.objects.get_or_create(
            card_number=card_number,
            defaults={"candidate_name": candidate_name, "feedbacks": []}
        )

        # Append new company feedback
        feedback_list = feedback_obj.feedbacks or []
        feedback_list.append(new_feedback)
        feedback_obj.feedbacks = feedback_list
        feedback_obj.save(update_fields=["feedbacks", "updated_at"])

        serializer = serializers.HRFeedbackSerializer(feedback_obj)
        return Response({
            "success": True,
            "message": "Feedback added successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "card_or_mobile",
                openapi.IN_PATH,
                description="16-digit card number or 10-digit mobile number",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: serializers.HRFeedbackSerializer()},
        tags=["HR Feedback"]
    )
    def get(self, request, card_or_mobile):
        """
        Fetch all feedbacks for a candidate using either card number or mobile number.
        """
        mbrcardno = None
        full_name = None
        if len(card_or_mobile) == 16 and card_or_mobile.isdigit():
            mbrcardno = card_or_mobile
        elif len(card_or_mobile) == 10 and card_or_mobile.isdigit():
            member_data = get_member_details_by_mobile(card_or_mobile)
            mbrcardno = member_data.get("mbrcardno") if member_data else None
            full_name = member_data.get("full_name") if member_data else None
        else:
            return Response({"success": False, "message": "Provide a valid 16-digit card number or 10-digit mobile number."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not mbrcardno:
            return Response({"success": False, "message": "Member not found."},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            feedback_obj = models.HRFeedback.objects.get(card_number=mbrcardno)
        except models.HRFeedback.DoesNotExist:
            return Response({"success": False,"candidate_name":full_name, "message": "No feedback found for this candidate."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.HRFeedbackSerializer(feedback_obj)
        data = serializer.data
         # Auto-fill candidate_name
        data["candidate_name"] = feedback_obj.candidate_name or full_name
        return Response({
            "success": True,
            "message": "Feedbacks fetched successfully.",
            "data": data
        }, status=status.HTTP_200_OK)
        
        
class HRFeedbackByBusinessAPIView(APIView):
    """
    List all candidate feedbacks given by the logged-in HR/business.
    """
    authentication_classes = [SSOBusinessTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Fetch all feedbacks submitted by the logged-in HR/business.",
        responses={
            200: openapi.Response(
                description="List of feedbacks",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Feedbacks given by business_id 102",
                        "count": 2,
                        "data": [
                            {
                                "card_number": "1234567890123456",
                                "candidate_name": "John Doe",
                                "feedbacks": [
                                    {
                                        "company_name": "ABC Tech",
                                        "job_title": "Developer",
                                        "employee_id": "EMP001",
                                        "feedback_questions": {"Q1": "Good"},
                                        "comments": "Excellent",
                                        "business_id": 102
                                    }
                                ]
                            }
                        ]
                    }
                }
            )
        },
        tags=["HR Feedback"]
    )
    def get(self, request):
        business_id = request.user.business_id

        all_feedbacks = models.HRFeedback.objects.all()
        filtered_feedbacks = []

        for fb in all_feedbacks:
            # Filter only feedbacks given by this business
            my_feedbacks = [f for f in (fb.feedbacks or []) if f.get("business_id") == business_id]
            if my_feedbacks:
                filtered_feedbacks.append({
                    "card_number": fb.card_number,
                    "candidate_name": fb.candidate_name,
                    "feedbacks": my_feedbacks
                })

        return Response({
            "success": True,
            "message": f"Feedbacks given by business_id {business_id}",
            "count": len(filtered_feedbacks),
            "data": filtered_feedbacks
        }, status=status.HTTP_200_OK)