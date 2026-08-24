from django.db import models
from django.contrib.auth.models import User

class CropDiseaseKnowledge(models.Model):
    crop_name = models.CharField(max_length=150)
    crop_name_native = models.CharField(max_length=150, blank=True)
    disease_name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200, blank=True)
    severity = models.CharField(max_length=100, default='Moderate')
    confidence_default = models.FloatField(default=95.0)
    symptoms = models.TextField(blank=True, default='')
    organic_solution = models.TextField(blank=True, default='')
    chemical_solution = models.TextField(blank=True, default='')
    prevention_advice = models.TextField(blank=True, default='')
    sample_image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_name} - {self.disease_name}"


class LeafScanHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leaf_scans')
    image = models.ImageField(upload_to='leaf_scans/', null=True, blank=True)
    crop_detected = models.CharField(max_length=150)
    crop_scientific_name = models.CharField(max_length=150, blank=True, default='')
    disease_detected = models.CharField(max_length=200)
    disease_scientific_name = models.CharField(max_length=200, blank=True, default='')
    category = models.CharField(max_length=100, default='Foliar Pathology')
    confidence_level = models.CharField(max_length=50, default='high')
    confidence = models.FloatField(default=95.0)
    severity = models.CharField(max_length=100, default='Moderate')
    source = models.CharField(max_length=100, default='claude_vision')
    status = models.CharField(max_length=50, default='success')
    symptoms = models.TextField(blank=True, default='')
    diagnosis_summary = models.TextField(blank=True, default='')
    organic_solution = models.TextField(blank=True, default='')
    chemical_solution = models.TextField(blank=True, default='')
    prevention_advice = models.TextField(blank=True, default='')
    warning = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan: {self.crop_detected} ({self.disease_detected}) [{self.source}] at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
