from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .ai_services.ai_trainer import AIModelTrainer
from .ai_services.dataset_manager import DatasetManager
from .ai_services.cv_analyzer import CVAnalyzer

trainer = AIModelTrainer()
dataset_manager = DatasetManager()

@csrf_exempt
@require_http_methods(["POST"])
def train_ai_model(request):
    try:
        data = json.loads(request.body)
        
        load_result = dataset_manager.load_dataset()
        if not load_result["success"]:
            return JsonResponse(load_result, status=500)
        
        prep_result = dataset_manager.preprocess_data()
        if not prep_result["success"]:
            return JsonResponse(prep_result, status=500)
        
        split_result = dataset_manager.get_train_test_split()
        if not split_result["success"]:
            return JsonResponse(split_result, status=500)
        
        train_result = trainer.train_model(
            split_result["X_train"], 
            split_result["y_train"],
            split_result["X_test"], 
            split_result["y_test"],
            epochs=data.get("epochs", 3)
        )
        
        return JsonResponse(train_result)
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def predict_cv_category(request):
    try:
        data = json.loads(request.body)
        cv_text = data.get("cv_text")
        
        if not cv_text:
            return JsonResponse({"error": "cv_text requis"}, status=400)
        
        prediction = trainer.predict(cv_text)
        return JsonResponse({"success": True, "prediction": prediction})
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def score_cv_job_match(request):
    try:
        data = json.loads(request.body)
        cv_text = data.get("cv_text")
        job_description = data.get("job_description")
        target_category = data.get("target_category")
        
        if not cv_text or not job_description:
            return JsonResponse({"error": "cv_text et job_description requis"}, status=400)
        
        score_result = trainer.score_cv_for_job(cv_text, job_description, target_category)
        return JsonResponse({"success": True, "scoring": score_result})
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_model_metrics(request):
    try:
        if not hasattr(trainer, 'model') or trainer.model is None:
            return JsonResponse({"error": "Modèle non entraîné"}, status=400)
        
        split_result = dataset_manager.get_train_test_split()
        if not split_result["success"]:
            return JsonResponse(split_result, status=500)
        
        test_dataset = trainer.tokenizer(
            list(split_result["X_test"]), 
            truncation=True, 
            padding=True, 
            return_tensors="pt"
        )
        
        metrics = trainer.evaluate(test_dataset)
        return JsonResponse({"success": True, "metrics": metrics})
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
