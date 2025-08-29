from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os

from .models import Resume, Candidate, JobPosition, CVAnalysis
from .ai_services.cv_analyzer import CVAnalyzer
from .ai_services.text_extractor import TextExtractor
from .ai_services.dataset_manager import DatasetManager

# Initialiser l'analyseur IA globalement
cv_analyzer = CVAnalyzer()

def index(request):
    return render(request, 'CVAnalyser/index.html')

def api_index(request):
    """Documentation de l'API REST"""
    api_endpoints = {
        "message": "🤖 API d'Analyse CV avec IA - Documentation",
        "version": "1.0.0",
        "status": "✅ Opérationnelle",
        "endpoints": {
            "🏠 Accueil": {
                "url": "/",
                "method": "GET",
                "description": "Interface web principale"
            },
            "🤖 Statut IA": {
                "url": "/api/ai-status/",
                "method": "GET", 
                "description": "Vérifier le statut des modèles IA"
            },
            "📤 Upload CV": {
                "url": "/api/upload-cv/",
                "method": "POST",
                "description": "Uploader et analyser un CV",
                "params": {
                    "cv_file": "Fichier CV (PDF, DOCX, TXT)",
                    "name": "Nom du candidat (optionnel)",
                    "email": "Email du candidat (optionnel)"
                }
            },
            "🎯 Analyse CV/Poste": {
                "url": "/api/analyze-cv-job/",
                "method": "POST",
                "description": "Calculer la correspondance CV/poste",
                "params": {
                    "resume_id": "ID du CV analysé",
                    "job_description": "Description du poste"
                }
            },
            "📋 Liste CV": {
                "url": "/api/resumes/",
                "method": "GET",
                "description": "Lister tous les CV analysés"
            },
            "📄 Détails CV": {
                "url": "/api/resume/{resume_id}/",
                "method": "GET",
                "description": "Obtenir les détails d'un CV spécifique"
            },
            "📊 Télécharger Dataset": {
                "url": "/api/download-dataset/",
                "method": "GET",
                "description": "Télécharger des datasets de CV depuis Kaggle"
            }
        },
        "formats_supportes": ["PDF", "DOCX", "TXT"],
        "ia_models": {
            "NER": "bert-large-cased-finetuned-conll03-english",
            "Similarity": "sentence-transformers/all-MiniLM-L6-v2"
        },
        "examples": {
            "test_ia": "GET /api/ai-status/",
            "upload_cv": "POST /api/upload-cv/ (avec fichier)",
            "liste_cv": "GET /api/resumes/"
        }
    }
    
    return JsonResponse(api_endpoints, json_dumps_params={'ensure_ascii': False, 'indent': 2})

@csrf_exempt
@require_http_methods(["POST"])
def upload_cv(request):
    try:
        if 'cv_file' not in request.FILES:
            return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)
        
        cv_file = request.FILES['cv_file']
        
        # Vérifier que les settings existent
        try:
            allowed_extensions = settings.ALLOWED_CV_EXTENSIONS
            max_size = settings.CV_UPLOAD_MAX_SIZE
        except AttributeError as e:
            return JsonResponse({'error': f'Configuration manquante: {e}'}, status=500)
        
        file_extension = os.path.splitext(cv_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'error': f'Format de fichier non supporté. Formats acceptés: {allowed_extensions}'
            }, status=400)
        
        if cv_file.size > max_size:
            return JsonResponse({
                'error': 'Fichier trop volumineux'
            }, status=400)
        
        candidate_email = request.POST.get('email', '')
        candidate_name = request.POST.get('name', 'Candidat Anonyme')
        
        # Créer ou récupérer le candidat
        try:
            if candidate_email:
                candidate, created = Candidate.objects.get_or_create(
                    email=candidate_email,
                    defaults={
                        'first_name': candidate_name.split()[0] if candidate_name.split() else 'Prénom',
                        'last_name': ' '.join(candidate_name.split()[1:]) if len(candidate_name.split()) > 1 else 'Nom'
                    }
                )
            else:
                candidate = Candidate.objects.create(
                    email=f"temp_{cv_file.name}_{cv_file.size}@temp.com",
                    first_name=candidate_name.split()[0] if candidate_name.split() else 'Prénom',
                    last_name=' '.join(candidate_name.split()[1:]) if len(candidate_name.split()) > 1 else 'Nom'
                )
        except Exception as e:
            return JsonResponse({'error': f'Erreur création candidat: {e}'}, status=500)
        
        # Sauvegarder le fichier
        try:
            file_path = default_storage.save(f'resumes/{cv_file.name}', cv_file)
            full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        except Exception as e:
            return JsonResponse({'error': f'Erreur sauvegarde fichier: {e}'}, status=500)
        
        # Créer l'enregistrement Resume
        try:
            resume = Resume.objects.create(
                candidate=candidate,
                file=file_path,
                original_filename=cv_file.name,
                file_size=cv_file.size,
                file_type=file_extension
            )
        except Exception as e:
            return JsonResponse({'error': f'Erreur création resume: {e}'}, status=500)
        
        # Extraction du texte
        try:
            extraction_result = TextExtractor.extract_and_clean(full_file_path)
            
            if not extraction_result['success']:
                resume.processing_error = extraction_result['error']
                resume.save()
                return JsonResponse({
                    'error': 'Erreur lors de l\'extraction du texte',
                    'details': extraction_result['error']
                }, status=500)
            
            resume.extracted_text = extraction_result['cleaned_text']
        except Exception as e:
            resume.processing_error = str(e)
            resume.save()
            return JsonResponse({'error': f'Erreur extraction texte: {e}'}, status=500)
        
        # Analyse IA
        try:
            analysis_result = cv_analyzer.extract_text_from_cv(extraction_result['cleaned_text'])
            
            resume.extracted_skills = analysis_result.get('skills', {})
            resume.extracted_experience = analysis_result.get('experience', {})
            resume.extracted_education = analysis_result.get('education', [])
            resume.extracted_languages = analysis_result.get('languages', [])
            resume.processed = True
            resume.save()
            
            return JsonResponse({
                'success': True,
                'resume_id': resume.id,
                'candidate_id': candidate.id,
                'extracted_data': analysis_result,
                'message': 'CV analysé avec succès'
            })
            
        except Exception as e:
            resume.processing_error = str(e)
            resume.save()
            return JsonResponse({
                'error': 'Erreur lors de l\'analyse IA',
                'details': str(e)
            }, status=500)
    
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur interne du serveur',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def analyze_cv_for_job(request):
    try:
        data = json.loads(request.body)
        resume_id = data.get('resume_id')
        job_description = data.get('job_description')
        
        if not resume_id or not job_description:
            return JsonResponse({
                'error': 'resume_id et job_description requis'
            }, status=400)
        
        resume = get_object_or_404(Resume, id=resume_id)
        
        if not resume.processed:
            return JsonResponse({
                'error': 'CV non traité'
            }, status=400)
        
        match_result = cv_analyzer.calculate_job_match_score(
            resume.extracted_text,
            job_description
        )
        
        if 'error' in match_result:
            return JsonResponse({
                'error': 'Erreur lors du calcul de correspondance',
                'details': match_result['error']
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'match_result': match_result
        })
    
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors de l\'analyse',
            'details': str(e)
        }, status=500)

def get_resume_details(request, resume_id):
    """
    Récupère les détails d'un CV analysé
    """
    try:
        resume = get_object_or_404(Resume, id=resume_id)
        
        return JsonResponse({
            'success': True,
            'resume': {
                'id': resume.id,
                'candidate': f"{resume.candidate.first_name} {resume.candidate.last_name}",
                'original_filename': resume.original_filename,
                'extracted_skills': resume.extracted_skills,
                'extracted_experience': resume.extracted_experience,
                'extracted_education': resume.extracted_education,
                'extracted_languages': resume.extracted_languages,
                'processed': resume.processed,
                'created_at': resume.created_at.isoformat()
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors de la récupération',
            'details': str(e)
        }, status=500)

def download_dataset(request):
    try:
        dataset_manager = DatasetManager()
        path = dataset_manager.download_kaggle_dataset()
        
        if path:
            df = dataset_manager.load_and_explore_dataset()
            
            return JsonResponse({
                'success': True,
                'dataset_path': path,
                'dataset_info': {
                    'rows': len(df) if df is not None else 0,
                    'columns': list(df.columns) if df is not None else []
                }
            })
        else:
            return JsonResponse({
                'error': 'Erreur lors du téléchargement du dataset'
            }, status=500)
    
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors du téléchargement',
            'details': str(e)
        }, status=500)

def list_resumes(request):
    resumes = Resume.objects.filter(processed=True).order_by('-created_at')
    
    resumes_data = []
    for resume in resumes:
        resumes_data.append({
            'id': resume.id,
            'candidate': f"{resume.candidate.first_name} {resume.candidate.last_name}",
            'original_filename': resume.original_filename,
            'skills_count': sum(len(skills) for skills in resume.extracted_skills.values()) if resume.extracted_skills else 0,
            'created_at': resume.created_at.isoformat()
        })
    
    return JsonResponse({
        'success': True,
        'resumes': resumes_data
    })

def ai_status(request):
    try:
        # tester l'analyseur
        test_text = "Test engineer with Python experience"
        result = cv_analyzer.extract_skills(test_text)
        
        return JsonResponse({
            'success': True,
            'ai_models_loaded': cv_analyzer.sentence_model is not None,
            'ner_pipeline_loaded': cv_analyzer.ner_pipeline is not None,
            'test_result': result
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
