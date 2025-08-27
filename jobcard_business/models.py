from django.db import models
from django.utils import timezone

class Job(models.Model):
    WORKPLACE_CHOICES = [
        ('On-site', 'On-site'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]

  

    RECRUITMENT_TIMELINE_CHOICES = [
        ("Immediate", "Immediate"),
        ("1 Week", "1 Week"),
        ("2 Weeks", "2 Weeks"),
        ("1 Month", "1 Month"),
        ("Flexible", "Flexible")
    ]

    EDUCATION_LEVEL_CHOICES = [
        ("10th Pass", "10th Pass"),
        ("12th Pass", "12th Pass"),
        ("ITI", "ITI"),
        ("Diploma", "Diploma"),
        ("Graduate", "Graduate"),
        ("Post Graduate", "Post Graduate"),
        ("Doctorate", "Doctorate"),
        ("MBA", "MBA"),
        ("Other", "Other"),
    ]

    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary'),
        ('Permanent', 'Permanent'),
    ]

    SCHEDULE_CHOICES = [
        ("Day shift", "Day shift"),
        ("Night shift", "Night shift"),
        ("Weekend availability", "Weekend availability"),
        ("Rotational shift", "Rotational shift"),
        ("Flexible shift", "Flexible shift"),
    ]

    EXPERIENCE_CHOICES = [
        ("Fresher", "Fresher"),
        ("0-1 Years", "0-1 Years"),
        ("1-3 Years", "1-3 Years"),
        ("3-5 Years", "3-5 Years"),
        ("5+ Years", "5+ Years"),
    ]

    INDUSTRY_CHOICES = [
        ("IT", "IT"),
        ("Education", "Education"),
        ("Healthcare", "Healthcare"),
        ("Finance", "Finance"),
        ("Retail", "Retail"),
        ("Construction", "Construction"),
        ("Manufacturing", "Manufacturing"),
        ("Hospitality", "Hospitality"),
    ]

    business_id = models.IntegerField(null=True, blank=True)

    # Step 0
    title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    workplace = models.CharField(max_length=20, choices=WORKPLACE_CHOICES)

    # Step 1
    job_type = models.JSONField(default=list, blank=True)
    schedule = models.JSONField(default=list, blank=True)
    number_of_posts = models.PositiveIntegerField()
    recruitment_timeline = models.CharField(max_length=20, choices=RECRUITMENT_TIMELINE_CHOICES)

    # Step 2
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pay_rate = models.CharField(max_length=20)
    key_skills = models.JSONField(default=list, blank=True)
    specialisations = models.JSONField(default=list, blank=True)

    # Step 3
    description = models.TextField(null=True, blank=True)
    company_info = models.TextField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)

    # Step 4
    education_levels = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)

    # Step 5
    application_end_date = models.DateField(null=True, blank=True)
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, default="IT")
    experience_required = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES)
    image = models.TextField(blank=True, null=True)
    video = models.TextField(blank=True, null=True)
    
    youtube_url = models.URLField(max_length=255, blank=True, null=True, help_text="YouTube video link")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    def check_and_deactivate(self):
        """Deactivate job if end date has passed"""
        if self.application_end_date and self.application_end_date < timezone.now().date():
            if self.is_active:
                self.is_active = False
                self.save(update_fields=["is_active"])

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
    referral = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of the employee who submitted the application"
    )

    def __str__(self):
        return f"{self.member_card} applied to {self.job.title}"

    

class Feedback(models.Model):
    HAPPINESS_CHOICES = [(i, str(i)) for i in range(1, 11)]  # 1 to 10 rating

    card_number = models.BigIntegerField(verbose_name="Member Card Number")
    business_id = models.IntegerField( verbose_name="Business ID", blank=True, null=True)
    happiness_rating = models.IntegerField(choices=HAPPINESS_CHOICES, verbose_name="Happiness Rating")
    has_issues = models.BooleanField(verbose_name="Facing any issues?")
    issues_detail = models.TextField(blank=True, null=True, verbose_name="Issue Details")
    liked_most = models.TextField(blank=True, null=True, verbose_name="What do you like most?")
    suggestions = models.TextField(blank=True, null=True, verbose_name="Suggestions for improvement")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_number} - {self.happiness_rating}/10"
    
    
class HRFeedback(models.Model):
    candidate_name = models.CharField(max_length=255, verbose_name="Candidate Name")
    card_number = models.BigIntegerField(unique=True, verbose_name="Card Number")  # unique per candidate
    feedbacks = models.JSONField(default=list,help_text="""Store multiple company feedbacks as a list of dicts. 
    Each dict can include company info, job info, feedback, comments, and business ID, e.g.:

    [
        {
            'company_name': 'ABC',
            'job_title': 'Developer',
            'employee_id': 'E123',
            'feedback_questions': {'Question 1': 'Answer'},
            'comments': 'Good candidate',
            'business_id': 101365
        },
   
    ]
    """
)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.card_number}"