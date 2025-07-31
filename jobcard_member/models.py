from django.db import models
from django.contrib.postgres.fields import JSONField
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
    
    
class Feedback(models.Model):
    card_number = models.BigIntegerField(
        unique=True,
        verbose_name="Member Card Number",
        null=True,
        blank=True
    )
    business_id = models.CharField(max_length=100)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    happiness_rating = models.IntegerField(blank=True, null=True)
    has_issues = models.BooleanField(blank=True, null=True)
    issues_description = models.TextField(blank=True, null=True)
    liked_most = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    answers = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.card_number})"