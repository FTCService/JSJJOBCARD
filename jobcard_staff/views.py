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


from .models import Campaign, CampaignAudience, EmailContent, SMSContent, WhatsAppContent, CampaignDeliveryLog
from .serializers import CampaignSerializer, CampaignAudienceSerializer, EmailContentSerializer, SMSContentSerializer, WhatsAppContentSerializer, CampaignDeliveryLogSerializer


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
            
            
            
            
            
class CampaignAPI(APIView):
    """
    Staff can view, create, and update campaigns.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all campaigns.",
        responses={200: CampaignSerializer(many=True)},
        tags=["Campaign"]
    )
    def get(self, request):
        try:
            campaigns = Campaign.objects.all()
            serializer = CampaignSerializer(campaigns, many=True)
            return Response({
                "success": True,
                "message": "Campaigns retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new campaign.",
        request_body=CampaignSerializer,
        responses={201: CampaignSerializer},
        tags=["Campaign"]
    )
    def post(self, request):
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Campaign created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CampaignDetailAPI(APIView):
    """
    Retrieve, update, or delete a campaign by its ID.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific campaign by ID.",
        responses={200: CampaignSerializer},
        tags=["Campaign"]
    )
    def get(self, request, campaign_id):
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            serializer = CampaignSerializer(campaign)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Campaign.DoesNotExist:
            return Response({
                "success": False,
                "message": "Campaign not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Update a specific campaign by ID.",
        request_body=CampaignSerializer,
        responses={200: CampaignSerializer},
        tags=["Campaign"]
    )
    def put(self, request, campaign_id):
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            serializer = CampaignSerializer(campaign, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Campaign updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Campaign.DoesNotExist:
            return Response({
                "success": False,
                "message": "Campaign not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a campaign by ID.",
        responses={
            204: openapi.Response(description="Campaign deleted successfully"),
            404: openapi.Response(description="Campaign not found")
        },
        tags=["Campaign"]
    )
    def delete(self, request, campaign_id):
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            campaign.delete()
            return Response({
                "success": True,
                "message": "Campaign deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except Campaign.DoesNotExist:
            return Response({
                "success": False,
                "message": "Campaign not found."
            }, status=status.HTTP_404_NOT_FOUND)


class CampaignAudienceCreateAPI(APIView):
    """
    Create a new Campaign Audience entry.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new campaign audience entry.",
        request_body=CampaignAudienceSerializer,
        responses={201: CampaignAudienceSerializer},
        tags=["Campaign Audience"]
    )
    def post(self, request):
        serializer = CampaignAudienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Audience created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CampaignAudienceDetailAPI(APIView):
    """
    Retrieve, update, or delete a Campaign Audience by ID.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific campaign audience by ID.",
        responses={200: CampaignAudienceSerializer},
        tags=["Campaign Audience"]
    )
    def get(self, request, audience_id):
        try:
            audience = CampaignAudience.objects.get(id=audience_id)
            serializer = CampaignAudienceSerializer(audience)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except CampaignAudience.DoesNotExist:
            return Response({
                "success": False,
                "message": "Audience not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Update a campaign audience by ID.",
        request_body=CampaignAudienceSerializer,
        responses={200: CampaignAudienceSerializer},
        tags=["Campaign Audience"]
    )
    def put(self, request, audience_id):
        try:
            audience = CampaignAudience.objects.get(id=audience_id)
            serializer = CampaignAudienceSerializer(audience, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Audience updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except CampaignAudience.DoesNotExist:
            return Response({
                "success": False,
                "message": "Audience not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Delete a campaign audience by ID.",
        responses={
            204: openapi.Response(description="Audience deleted successfully"),
            404: openapi.Response(description="Audience not found")
        },
        tags=["Campaign Audience"]
    )
    def delete(self, request, audience_id):
        try:
            audience = CampaignAudience.objects.get(id=audience_id)
            audience.delete()
            return Response({
                "success": True,
                "message": "Audience deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except CampaignAudience.DoesNotExist:
            return Response({
                "success": False,
                "message": "Audience not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
            
class EmailContentCreateAPI(APIView):
    """
    Create Email Content for a Campaign.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create email content for a campaign.",
        request_body=EmailContentSerializer,
        responses={201: EmailContentSerializer},
        tags=["Email Content"]
    )
    def post(self, request):
        serializer = EmailContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Email content created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class EmailContentDetailAPI(APIView):
    """
    Retrieve, update, or delete Email Content by Campaign ID.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve email content by campaign ID.",
        responses={200: EmailContentSerializer},
        tags=["Email Content"]
    )
    def get(self, request, campaign_id):
        try:
            content = EmailContent.objects.get(campaign_id=campaign_id)
            serializer = EmailContentSerializer(content)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except EmailContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "Email content not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Update email content by campaign ID.",
        request_body=EmailContentSerializer,
        responses={200: EmailContentSerializer},
        tags=["Email Content"]
    )
    def put(self, request, campaign_id):
        try:
            content = EmailContent.objects.get(campaign_id=campaign_id)
            serializer = EmailContentSerializer(content, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Email content updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except EmailContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "Email content not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Delete email content by campaign ID.",
        responses={
            204: openapi.Response(description="Email content deleted successfully"),
            404: openapi.Response(description="Email content not found")
        },
        tags=["Email Content"]
    )
    def delete(self, request, campaign_id):
        try:
            content = EmailContent.objects.get(campaign_id=campaign_id)
            content.delete()
            return Response({
                "success": True,
                "message": "Email content deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except EmailContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "Email content not found."
            }, status=status.HTTP_404_NOT_FOUND)
            

class SMSContentCreateAPI(APIView):
    """
    Create SMS content for a campaign.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create SMS content for a campaign.",
        request_body=SMSContentSerializer,
        responses={201: SMSContentSerializer},
        tags=["SMS Content"]
    )
    def post(self, request):
        campaign_id = request.data.get("campaign")
        if SMSContent.objects.filter(campaign_id=campaign_id).exists():
            return Response({
                "success": False,
                "message": "SMS content for this campaign already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = SMSContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "SMS content created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SMSContentDetailAPI(APIView):
    """
    Retrieve, update, or delete SMS content by campaign ID.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve SMS content by campaign ID.",
        responses={200: SMSContentSerializer},
        tags=["SMS Content"]
    )
    def get(self, request, campaign_id):
        try:
            content = SMSContent.objects.get(campaign_id=campaign_id)
            serializer = SMSContentSerializer(content)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except SMSContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "SMS content not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Update SMS content by campaign ID.",
        request_body=SMSContentSerializer,
        responses={200: SMSContentSerializer},
        tags=["SMS Content"]
    )
    def put(self, request, campaign_id):
        try:
            content = SMSContent.objects.get(campaign_id=campaign_id)
            serializer = SMSContentSerializer(content, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "SMS content updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except SMSContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "SMS content not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Delete SMS content by campaign ID.",
        responses={
            204: openapi.Response(description="SMS content deleted successfully"),
            404: openapi.Response(description="SMS content not found")
        },
        tags=["SMS Content"]
    )
    def delete(self, request, campaign_id):
        try:
            content = SMSContent.objects.get(campaign_id=campaign_id)
            content.delete()
            return Response({
                "success": True,
                "message": "SMS content deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except SMSContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "SMS content not found."
            }, status=status.HTTP_404_NOT_FOUND)
            

class WhatsAppContentCreateAPI(APIView):
    """
    Create WhatsApp content for a campaign.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create WhatsApp content for a campaign.",
        request_body=WhatsAppContentSerializer,
        responses={201: WhatsAppContentSerializer},
        tags=["WhatsApp Content"]
    )
    def post(self, request):
        campaign_id = request.data.get("campaign")
        if WhatsAppContent.objects.filter(campaign_id=campaign_id).exists():
            return Response({
                "success": False,
                "message": "WhatsApp content for this campaign already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = WhatsAppContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "WhatsApp content created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class WhatsAppContentDetailAPI(APIView):
    """
    Retrieve, update, or delete WhatsApp content by campaign ID.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve WhatsApp content by campaign ID.",
        responses={200: WhatsAppContentSerializer},
        tags=["WhatsApp Content"]
    )
    def get(self, request, campaign_id):
        try:
            content = WhatsAppContent.objects.get(campaign_id=campaign_id)
            serializer = WhatsAppContentSerializer(content)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except WhatsAppContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "WhatsApp content not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Update WhatsApp content by campaign ID.",
        request_body=WhatsAppContentSerializer,
        responses={200: WhatsAppContentSerializer},
        tags=["WhatsApp Content"]
    )
    def put(self, request, campaign_id):
        try:
            content = WhatsAppContent.objects.get(campaign_id=campaign_id)
            serializer = WhatsAppContentSerializer(content, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "WhatsApp content updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except WhatsAppContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "WhatsApp content not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Delete WhatsApp content by campaign ID.",
        responses={
            204: openapi.Response(description="WhatsApp content deleted successfully"),
            404: openapi.Response(description="WhatsApp content not found")
        },
        tags=["WhatsApp Content"]
    )
    def delete(self, request, campaign_id):
        try:
            content = WhatsAppContent.objects.get(campaign_id=campaign_id)
            content.delete()
            return Response({
                "success": True,
                "message": "WhatsApp content deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except WhatsAppContent.DoesNotExist:
            return Response({
                "success": False,
                "message": "WhatsApp content not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
class CampaignDeliveryLogCreateAPI(APIView):
    """
    Create a delivery log entry for a campaign.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new delivery log for a campaign.",
        request_body=CampaignDeliveryLogSerializer,
        responses={201: CampaignDeliveryLogSerializer},
        tags=["Campaign Delivery Log"]
    )
    def post(self, request):
        serializer = CampaignDeliveryLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Delivery log created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CampaignDeliveryLogListAPI(APIView):
    """
    List all delivery logs for a specific campaign.
    """
    authentication_classes = [SSOUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all delivery logs for a campaign.",
        responses={200: CampaignDeliveryLogSerializer(many=True)},
        tags=["Campaign Delivery Log"]
    )
    def get(self, request, campaign_id):
        logs = CampaignDeliveryLog.objects.filter(campaign_id=campaign_id)
        serializer = CampaignDeliveryLogSerializer(logs, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)