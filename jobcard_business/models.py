from django.db import models

class JobApplication(models.Model):
    candidate_name = models.CharField(max_length=100)
    candidate_email = models.EmailField()
    member_id = models.CharField(max_length=50)  # Student card number
    location = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} applied to {self.job.title}"