from django.db import models

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
    
    
from django.db import models

class Education(models.Model):
    education_id = models.CharField(max_length=50)  # e.g., "12th", "bachelors", "iti"
    education_name = models.CharField(max_length=200)  # e.g., "Bachelor's Degree"
    education_description = models.TextField(blank=True, null=True)

    specialization_id = models.CharField(max_length=100, unique=True)  # e.g., "bsc-maths", "electrician"
    specialization_name = models.CharField(max_length=200)
    specialization_description = models.TextField(blank=True, null=True)
    eligibility = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)  # e.g., Engineering, Science, Arts

    def __str__(self):
        return f"{self.specialization_name} ({self.education_name})"
