from django.db import models

class GovtScheme(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    category = models.CharField(max_length=100, default='Central Scheme')
    benefit_amount = models.CharField(max_length=150)
    eligibility = models.TextField()
    required_documents = models.JSONField(default=list)
    application_status = models.CharField(max_length=100, default='Applications Open')
    official_portal_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
