from django.db import models
from django.utils import timezone
from datetime import timedelta
class MbrDocuments(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("verified", "Verified"),
    ]
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
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