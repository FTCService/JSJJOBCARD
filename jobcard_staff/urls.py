from django.urls import path
from . import  views, job_mitra_api
from .Inquiry_api import InquiryListCreateAPI


urlpatterns = [
    path("jobs-list/post/", views.JobListCreateAPIView.as_view(), name="job-list-create"),
    path("jobs-details/<int:id>/", views.JobDetailAPIView.as_view(), name="job-detail"),
    path('job-applications/<int:job_id>/', views.JobApplicationListOfStudent.as_view(), name='job-applications-by-job'),
    path('staff/member-documents/<str:card_number>/', views.MbrDocumentsAPI.as_view(), name='member-documents'),
    
    
    
    path('job_mitra/applied/list/<int:job_id>/', job_mitra_api.ApplicationListOfStudent.as_view(), name='job_mitra-applied-list'),
    path('jobmitra/member-details/', job_mitra_api.GetMemberDetailsByCardApi.as_view(), name='get-member-details'),
    path('jobmitra/apply-for-member/', job_mitra_api.ApplyJobForMemberAPIView.as_view(), name='apply-job-for-member'),
    
    
    # ✅ Campaign endpoints (new)
    path('campaigns/', views.CampaignAPI.as_view(), name='campaign-list-create'),
    path('campaigns/<int:campaign_id>/', views.CampaignDetailAPI.as_view(), name='campaign-detail'),
    
    # ✅ Campaign Audience endpoints
    path('campaign-audience/create/', views.CampaignAudienceCreateAPI.as_view(), name='campaign-audience-create'),
    path('campaign-audience/<int:audience_id>/', views.CampaignAudienceDetailAPI.as_view(), name='campaign-audience-detail'),
    
    # 🔹 Email Content endpoints (NEW)
    path('email-content/create/', views.EmailContentCreateAPI.as_view(), name='email-content-create'),
    path('email-content/<int:campaign_id>/', views.EmailContentDetailAPI.as_view(), name='email-content-detail'),
    
    # 🔹 SMS Content endpoints
    path('sms-content/create/', views.SMSContentCreateAPI.as_view(), name='sms-content-create'),
    path('sms-content/<int:campaign_id>/', views.SMSContentDetailAPI.as_view(), name='sms-content-detail'),
    
    # 🔹 WhatsApp Content endpoints
    path('whatsapp-content/create/', views.WhatsAppContentCreateAPI.as_view(), name='whatsapp-content-create'),
    path('whatsapp-content/<int:campaign_id>/', views.WhatsAppContentDetailAPI.as_view(), name='whatsapp-content-detail'),
    
    # 🔹 Campaign Delivery Log endpoints
    path('campaign-delivery-log/create/', views.CampaignDeliveryLogCreateAPI.as_view(), name='campaign-delivery-log-create'),
    path('campaign-delivery-log/<int:campaign_id>/', views.CampaignDeliveryLogListAPI.as_view(), name='campaign-delivery-log-list'),
    
    path('inquiries/', InquiryListCreateAPI.as_view(), name='inquiry-list-create'),



]



