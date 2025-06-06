from django.db import models


class Document(models.Model):
    member = models.BigIntegerField(verbose_name=" member cardnumber", null=True, blank=True)

    # Certificates
    tenth_certificate = models.TextField(null=True, blank=True)
    twelfth_certificate = models.TextField(null=True, blank=True)
    graduation_certificate = models.TextField(null=True, blank=True)
    pg_certificate = models.TextField(null=True, blank=True)
    graduation_marksheet = models.TextField(null=True, blank=True)

    # Certifications
    technical_certification = models.TextField(null=True, blank=True)
    language_certification = models.TextField(null=True, blank=True)
    soft_skill_certification = models.TextField(null=True, blank=True)

    # Identity Docs
    aadhaar_card = models.TextField(null=True, blank=True)
    pan_card = models.TextField(null=True, blank=True)
    passport = models.TextField(null=True, blank=True)
    driving_license = models.TextField(null=True, blank=True)

    # Online Profiles
    linkedin_url = models.URLField(max_length=255, null=True, blank=True)
    github_url = models.URLField(max_length=255, null=True, blank=True)
    portfolio_website = models.URLField(max_length=255, null=True, blank=True)

    # Others
    resume = models.TextField(null=True, blank=True)
    offer_letter = models.TextField(null=True, blank=True)
    personal_statement = models.TextField(null=True, blank=True)

  
    

