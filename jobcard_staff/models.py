from django.db import models

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    ]

    title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    employer_id = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100)  # e.g., Remote, On-site
    staff_email = models.EmailField()
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

    # New fields for media
    image = models.ImageField(upload_to='job_images/', null=True, blank=True)
    video = models.FileField(upload_to='job_videos/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    

# job/models.py
class JobApplication(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='applications')
    candidate_name = models.CharField(max_length=100)
    candidate_email = models.EmailField()
    member_id = models.CharField(max_length=50)  # ✅ New field
    location = models.CharField(max_length=100)  # ✅ New field
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} applied for {self.job.title}"
    
