from django.db import models
from django.contrib.auth.models import User
import json

class JobPosition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.JSONField(default=list)
    required_experience_years = models.IntegerField(default=0)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Resume(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True)
    
    extracted_skills = models.JSONField(default=list)
    extracted_experience = models.JSONField(default=list)
    extracted_education = models.JSONField(default=list)
    extracted_languages = models.JSONField(default=list)
    
    file_size = models.IntegerField(default=0)
    file_type = models.CharField(max_length=10)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CV de {self.candidate} - {self.original_filename}"

class CVAnalysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='cv_analyses')
    
    overall_score = models.FloatField(default=0.0)
    skills_match_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    analysis_details = models.JSONField(default=dict)
    
    recommendations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['resume', 'job_position']
        ordering = ['-overall_score']

    def __str__(self):
        return f"Analyse: {self.resume.candidate} pour {self.job_position.title} ({self.overall_score}%)"

class AIModel(models.Model):
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=50, choices=[
        ('transformer', 'Transformer'),
        ('bert', 'BERT'),
        ('gpt', 'GPT'),
        ('sentence_transformer', 'Sentence Transformer'),
    ])
    model_path = models.CharField(max_length=500)
    version = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.model_type})"
