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
from jobcard_member.serializers import MbrDocumentsSerializer



class JobListCreateAPIView(APIView):
    """
    API to list all jobs or create a new job post.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all job postings.",
        responses={200: serializers.JobpostSerializer(many=True)},tags=["Staff"]
    )
    def get(self, request):
        try:
            jobs = Job.objects.all()
            serializer = serializers.JobpostSerializer(jobs, many=True)
            return Response({
                "success": True,
                "message": "Job list retrieved successfully.",
                "data": serializer.data
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
                
                # Example user info (replace with actual user fields as needed)
                full_name = "John Doe"
                email = "john.doe@example.com"

                context = {
                    "full_name": full_name,
                    "job_title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_url": f"https://jobportal.com/jobs/{job.id}",
                    "logo_url": "https://yourdomain.com/static/jsjlogo-jobcard.png"
                }

                send_template_email(
                    subject="New Job Alert Just for You - JSJCard",
                    template_name="email_template/job_post.html",
                    context=context,
                    recipient_list=[email]
                )
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
            
            # === Send Email Notification ===
            user = application.user
            full_name = user.get_full_name()
            email = user.email
            view_url = f"https://yourdomain.com/student/applications/{application.id}/"

            context = {
                "full_name": full_name,
                "application_id": application.id,
                "status": application.status,
                "view_url": view_url
            }

            subject = "📢 Application Status Updated - JSJCard"
            from_email = "noreply@yourdomain.com"
            to = [email]
            html_content = render_to_string("email_template/student_status.html", context)

            msg = EmailMultiAlternatives(subject, "", from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

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
            
