from django.db import models
from django.utils import timezone

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        
    ]
    business_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100)  # e.g., Remote, On-site
    application_end_date = models.DateField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
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
    experience_required = models.CharField(max_length=50, blank=True) 
    is_active = models.BooleanField(default=True)

    # New fields for media
    image = models.TextField( null=True, blank=True)
    video = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    

# job/models.py
class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    member_card =  models.BigIntegerField(verbose_name="Member Card Number")
    institute_id = models.IntegerField(verbose_name="Institute ID" , null=True, blank=True)
    cover_letter = models.TextField(blank=True)
    resume = models.TextField(max_length=255)
    applied_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=50,
        choices=[
            ('applied', 'Applied'),
            ('under_review', 'Under Review'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('selected', 'Selected')
        ],
        default='applied'
    )

    def __str__(self):
        return f"{self.member_card} applied to {self.job.title}"

    
