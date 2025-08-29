from django.urls import path
from . import views, ai_views

app_name = 'CVAnalyser'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Documentation API
    path('api/', views.api_index, name='api_index'),
    
    path('api/upload-cv/', views.upload_cv, name='upload_cv'),
    path('api/analyze-cv-job/', views.analyze_cv_for_job, name='analyze_cv_for_job'),
    path('api/resume/<int:resume_id>/', views.get_resume_details, name='resume_details'),
    path('api/resumes/', views.list_resumes, name='list_resumes'),
    
    path('api/download-dataset/', views.download_dataset, name='download_dataset'),
    
    path('api/ai-status/', views.ai_status, name='ai_status'),
    
    # AI Training API
    path('api/train-model/', ai_views.train_ai_model, name='train_model'),
    path('api/predict-category/', ai_views.predict_cv_category, name='predict_category'),
    path('api/score-cv-job/', ai_views.score_cv_job_match, name='score_cv_job'),
    path('api/model-metrics/', ai_views.get_model_metrics, name='model_metrics'),
]
