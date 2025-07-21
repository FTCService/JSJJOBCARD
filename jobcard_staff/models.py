# from django.db import models



# class Campaign(models.Model):
#     CAMPAIGN_TYPE_CHOICES = [
#         ('email', 'Email'),
#         ('sms', 'SMS'),
#         ('whatsapp', 'WhatsApp'),
#     ]
    
#     name = models.CharField(max_length=255)
#     campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
#     created_by = models.TextField( on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     scheduled_at = models.DateTimeField(null=True, blank=True)
#     is_sent = models.BooleanField(default=False)

#     def __str__(self):
#         return self.name


# class CampaignAudience(models.Model):
#     campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='audiences')
#     user = models.TextField()
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('campaign', 'user')


# class EmailContent(models.Model):
#     campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE)
#     subject = models.CharField(max_length=255)
#     body = models.TextField()
#     footer = models.TextField(blank=True, null=True)



# class SMSContent(models.Model):
#     campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE)
#     message = models.CharField(max_length=160)



# class WhatsAppContent(models.Model):
#     campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE)
#     template_name = models.CharField(max_length=100)
#     message_parameters = models.JSONField()  # key-value placeholders for personalization




# class CampaignDeliveryLog(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('sent', 'Sent'),
#         ('failed', 'Failed'),
#         ('read', 'Read'),  # for email and WhatsApp
#     ]
    
#     campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
#     user = models.TextField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     sent_at = models.DateTimeField(null=True, blank=True)
#     response_data = models.JSONField(blank=True, null=True)  # store raw API responses
