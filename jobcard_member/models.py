from django.db import models
from django.utils import timezone
from datetime import timedelta
class MbrDocuments(models.Model):

    card_number = models.BigIntegerField(unique=True, verbose_name="Member Card Number", null=True, blank=True)
    TenthCertificate = models.TextField(blank=True, null=True)
    TwelfthCertificate = models.TextField(blank=True, null=True)
    GraduationCertificate = models.TextField(blank=True, null=True)
    GraduationMarksheet = models.TextField(blank=True, null=True)
    PgCertificate = models.TextField(blank=True, null=True)
    UpskillCertificate = models.TextField(blank=True, null=True)
    ItiCertificate = models.TextField(blank=True, null=True)
    ItiMarksheet = models.TextField(blank=True, null=True)
    DiplomaCertificate = models.TextField(blank=True, null=True)
    DiplomaMarksheet = models.TextField(blank=True, null=True)
    CoverLetter = models.TextField(blank=True, null=True)
    Resume = models.TextField(blank=True, null=True)
    # Status field
    document_status = models.JSONField(
        default=dict,
        help_text="Store status of each document individually, e.g., {'Resume': 'verified', 'TenthCertificate': 'pending'}"
    )
    # Links
    AdharcardVoterid = models.TextField(blank=True, null=True)
    LinkedinUrl = models.URLField(blank=True, null=True)
    GithubUrl = models.URLField(blank=True, null=True)
    OtherLink = models.URLField(blank=True, null=True)

    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)
    
    
class DocumentAccess(models.Model):
    member = models.ForeignKey(MbrDocuments, on_delete=models.CASCADE)
    selected_fields = models.JSONField()  # Store field names selected
    pin = models.CharField(max_length=10)
    expiry_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.expiry_time
    
    

class DocumentVerificationRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    card_number = models.BigIntegerField(verbose_name="Member Card Number")
    requested_by = models.IntegerField(verbose_name="Business/HR ID")  # HR or business requesting
    documents = models.JSONField(
        default=dict,
        help_text="List of documents requested for verification with initial status, e.g., {'Resume': 'pending', 'TenthCertificate': 'pending'}"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.card_number} requested by {self.requested_by}"
