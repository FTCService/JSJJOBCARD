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

# models.py

class JobPost(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    employer_id = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100)  # e.g., Remote, On-site
    staff_email = models.EmailField()
    application_end_date = models.DateField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    requirements = models.TextField()
    about_company = models.TextField()
    description = models.TextField()
    languages = models.JSONField(default=list, blank=True)
    area_of_work = models.JSONField(default=list, blank=True)
    industry = models.CharField(max_length=100)
    number_of_posts = models.PositiveIntegerField()
    education_levels = models.JSONField(default=list, blank=True)
    specialisations = models.JSONField(default=list, blank=True)
    key_skills = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='job_images/', null=True, blank=True)
    video = models.FileField(upload_to='job_videos/', null=True, blank=True)

    def __str__(self):
        return self.title
    
class JobApplication(models.Model):
    candidate_name = models.CharField(max_length=100)
    candidate_email = models.EmailField()
    member_id = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} applied to {self.job.title}"


