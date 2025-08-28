#!/usr/bin/env python3
"""
Script de test d'intégration pour l'équipe
Vérifie que toute l'installation fonctionne correctement
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_status(message, status="INFO"):
    """Affiche un message avec statut coloré"""
    colors = {
        "SUCCESS": "\033[92m✅",
        "ERROR": "\033[91m❌", 
        "WARNING": "\033[93m⚠️",
        "INFO": "\033[94mℹ️"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def test_python_version():
    """Vérifie la version Python"""
    print_status("Test de la version Python...", "INFO")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor} - Version 3.8+ requise", "ERROR")
        return False

def test_virtual_environment():
    """Vérifie l'environnement virtuel"""
    print_status("Test de l'environnement virtuel...", "INFO")
    
    venv_paths = [
        Path(".venv"),
        Path("venv"),
        Path("env")
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists():
            print_status(f"Environnement virtuel trouvé: {venv_path}", "SUCCESS")
            return True
    
    print_status("Aucun environnement virtuel trouvé", "WARNING")
    return False

def test_django_installation():
    """Vérifie l'installation Django"""
    print_status("Test de l'installation Django...", "INFO")
    
    try:
        import django
        print_status(f"Django {django.get_version()} ✓", "SUCCESS")
        return True
    except ImportError:
        print_status("Django non installé", "ERROR")
        return False

def test_ai_packages():
    """Vérifie les packages IA"""
    print_status("Test des packages IA...", "INFO")
    
    packages = {
        "torch": "PyTorch",
        "transformers": "Transformers",
        "sentence_transformers": "Sentence Transformers",
        "nltk": "NLTK",
        "sklearn": "Scikit-learn"
    }
    
    success = True
    for package, name in packages.items():
        try:
            __import__(package)
            print_status(f"{name} ✓", "SUCCESS")
        except ImportError:
            print_status(f"{name} non installé", "ERROR")
            success = False
    
    return success

def test_django_project():
    """Vérifie la structure du projet Django"""
    print_status("Test de la structure du projet...", "INFO")
    
    required_files = [
        "CVAnalyserProject/manage.py",
        "CVAnalyserProject/CVAnalyser/models.py",
        "CVAnalyserProject/CVAnalyser/views.py",
        "CVAnalyserProject/CVAnalyser/ai_services/cv_analyzer.py",
        "CVAnalyserProject/CVAnalyser/ai_services/text_extractor.py"
    ]
    
    success = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_status(f"{file_path} ✓", "SUCCESS")
        else:
            print_status(f"{file_path} manquant", "ERROR")
            success = False
    
    return success

def start_django_server():
    """Lance le serveur Django en arrière-plan"""
    print_status("Lancement du serveur Django...", "INFO")
    
    os.chdir("CVAnalyserProject")
    
    try:
        # Lancer le serveur en arrière-plan
        process = subprocess.Popen([
            sys.executable, "manage.py", "runserver", "127.0.0.1:8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        print_status("Attente du démarrage du serveur (30s max)...", "INFO")
        
        for i in range(30):
            try:
                response = requests.get("http://127.0.0.1:8000/", timeout=1)
                if response.status_code == 200:
                    print_status("Serveur Django démarré ✓", "SUCCESS")
                    return process
            except:
                pass
            time.sleep(1)
        
        print_status("Timeout - Serveur non démarré", "ERROR")
        process.terminate()
        return None
        
    except Exception as e:
        print_status(f"Erreur lors du lancement: {e}", "ERROR")
        return None

def test_ai_api():
    """Teste l'API IA"""
    print_status("Test de l'API IA...", "INFO")
    
    try:
        # Test du statut de l'IA
        response = requests.get("http://127.0.0.1:8000/api/ai-status/", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_status("API IA fonctionnelle ✓", "SUCCESS")
                print_status(f"Modèles chargés: {', '.join(data.get('models_loaded', []))}", "INFO")
                return True
            else:
                print_status("IA non initialisée", "ERROR")
                return False
        else:
            print_status(f"Erreur HTTP {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Erreur API: {e}", "ERROR")
        return False

def test_cv_analysis():
    """Teste l'analyse de CV"""
    print_status("Test de l'analyse de CV...", "INFO")
    
    # CV de test simple
    test_cv = """
    Jean Dupont
    Développeur Python Senior
    
    Compétences:
    - Python, Django, Flask
    - Machine Learning, TensorFlow
    - SQL, PostgreSQL
    - Git, Docker
    
    Expérience:
    - 5 ans développement web
    - 2 ans intelligence artificielle
    """
    
    try:
        # Analyser le CV de test
        files = {'cv_file': ('test_cv.txt', test_cv, 'text/plain')}
        response = requests.post(
            "http://127.0.0.1:8000/api/upload-cv/", 
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_status("Analyse de CV réussie ✓", "SUCCESS")
                
                # Afficher quelques résultats
                extracted_data = data.get("extracted_data", {})
                skills = extracted_data.get("skills", [])
                experience = extracted_data.get("experience", [])
                
                print_status(f"Compétences extraites: {len(skills)}", "INFO")
                print_status(f"Expériences extraites: {len(experience)}", "INFO")
                
                return True
            else:
                print_status("Échec de l'analyse", "ERROR")
                return False
        else:
            print_status(f"Erreur HTTP {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Erreur analyse: {e}", "ERROR")
        return False

def main():
    """Fonction principale de test"""
    print("="*60)
    print("🧪 TESTS D'INTÉGRATION - ANALYSE CV IA")
    print("="*60)
    
    tests = [
        ("Version Python", test_python_version),
        ("Environnement virtuel", test_virtual_environment),
        ("Installation Django", test_django_installation),
        ("Packages IA", test_ai_packages),
        ("Structure projet", test_django_project)
    ]
    
    # Tests statiques
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    # Tests dynamiques (serveur)
    print(f"\n--- Test serveur Django ---")
    server_process = start_django_server()
    
    if server_process:
        # Tests API
        api_tests = [
            ("API IA", test_ai_api),
            ("Analyse CV", test_cv_analysis)
        ]
        
        for test_name, test_func in api_tests:
            print(f"\n--- {test_name} ---")
            result = test_func()
            results.append((test_name, result))
        
        # Arrêter le serveur
        print_status("Arrêt du serveur...", "INFO")
        server_process.terminate()
        server_process.wait()
    else:
        results.append(("Serveur Django", False))
        results.append(("API IA", False))
        results.append(("Analyse CV", False))
    
    # Rapport final
    print("\n" + "="*60)
    print("📊 RAPPORT FINAL")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "SUCCESS" if result else "ERROR"
        print_status(f"{test_name}: {'PASSÉ' if result else 'ÉCHEC'}", status)
    
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print_status("🎉 INSTALLATION COMPLÈTE ET FONCTIONNELLE!", "SUCCESS")
        print_status("L'équipe peut commencer à utiliser l'IA pour analyser les CV", "SUCCESS")
        return 0
    else:
        print_status("⚠️ Problèmes détectés - Voir les erreurs ci-dessus", "ERROR")
        print_status("Relancer 'python install_project.py' ou contacter le support", "WARNING")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
