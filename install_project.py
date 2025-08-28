#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description, check=True):
    print(f"\n{description}")
    print(f"Commande: {command}")
    
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:  # Linux/Mac
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.stdout:
            print("Sortie:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur:")
        print(e.stderr if e.stderr else e.stdout)
        return False

def check_python_version():
    print("Vérification de Python")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"Python {version.major}.{version.minor} - Version trop ancienne")
        print("   Minimum requis: Python 3.8+")
        return False

def create_virtual_environment():
    print("\nCréation de l'environnement virtuel...")
    
    if Path(".venv").exists():
        print("Environnement virtuel déjà existant")
        return True
    
    return run_command("python -m venv .venv", "Création de l'environnement virtuel")

def activate_and_install():
    print("\nInstallation des dépendances...")
    
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip.exe"
        python_cmd = ".venv\\Scripts\\python.exe"
    else:  # Linux/Mac
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    run_command(f"{pip_cmd} install --upgrade pip", "Mise à jour de pip")
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installation des packages Python"):
        return False
    
    print("Toutes les dépendances installées!")
    return True

def setup_django():
    print("\nConfiguration de Django...")
    
    if os.name == 'nt':  # Windows
        python_cmd = ".venv\\Scripts\\python.exe"
    else:  # Linux/Mac
        python_cmd = ".venv/bin/python"
    
    os.chdir("CVAnalyserProject")
    
    if not run_command(f"{python_cmd} manage.py makemigrations", "Création des migrations"):
        return False
    
    if not run_command(f"{python_cmd} manage.py migrate", "Application des migrations"):
        return False
    
    folders = ["media", "media/resumes", "ai_models", "datasets"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"📁 Dossier créé: {folder}")
    
    os.chdir("..")
    return True

def test_ai_components():
    print("\n🤖 Test des composants IA...")
    
    if os.name == 'nt':  # Windows
        python_cmd = ".venv\\Scripts\\python.exe"
    else:  # Linux/Mac
        python_cmd = ".venv/bin/python"
    
    test_code = """
try:
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    import nltk
    print("Tous les packages IA sont installés correctement")
except ImportError as e:
    print(f"Erreur d'import: {e}")
    exit(1)
"""
    
    with open("test_imports.py", "w") as f:
        f.write(test_code)
    
    success = run_command(f"{python_cmd} test_imports.py", "Test des imports IA")
    os.remove("test_imports.py")
    
    return success

def create_run_script():
    """Crée un script de lancement facile"""
    print("\nCréation du script de lancement...")
    
    if os.name == 'nt':  # Windows
        script_content = '''@echo off
echo Lancement du serveur Django avec IA...
cd CVAnalyserProject
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause
'''
        with open("start_server.bat", "w") as f:
            f.write(script_content)
        print("Script créé: start_server.bat")
    else:  # Linux/Mac
        script_content = '''#!/bin/bash
echo "Lancement du serveur Django avec IA..."
cd CVAnalyserProject
../.venv/bin/python manage.py runserver 127.0.0.1:8000
'''
        with open("start_server.sh", "w") as f:
            f.write(script_content)
        os.chmod("start_server.sh", 0o755)
        print("Script créé: start_server.sh")

def main():
    """Installation complète"""
    print("=" * 60)
    print("INSTALLATION AUTOMATIQUE - PROJET DJANGO + IA")
    print("=" * 60)
    
    # Vérifications
    if not check_python_version():
        return False
    
    # Installation
    steps = [
        (create_virtual_environment, "Environnement virtuel"),
        (activate_and_install, "Installation des dépendances"),
        (setup_django, "Configuration Django"),
        (test_ai_components, "Test des composants IA"),
        (create_run_script, "Script de lancement")
    ]
    
    for step_func, step_name in steps:
        if not step_func():
            print(f"\nÉchec lors de: {step_name}")
            return False
    
    # Instructions finales
    print("\n" + "=" * 60)
    print("INSTALLATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 60)
    
    print("\nPour démarrer le serveur:")
    if os.name == 'nt':
        print("   Double-cliquez sur: start_server.bat")
        print("   OU en ligne de commande: .venv\\Scripts\\python.exe CVAnalyserProject\\manage.py runserver")
    else:
        print("   Exécutez: ./start_server.sh")
        print("   OU en ligne de commande: .venv/bin/python CVAnalyserProject/manage.py runserver")
    
    print(f"\nInterface web: http://127.0.0.1:8000/")
    print(f"API status: http://127.0.0.1:8000/api/ai-status/")
    
    print("\n⏱IMPORTANT:")
    print(" Premier lancement: L'IA met 1-2 minutes à se charger")
    print(" Les modèles (1.4GB) se téléchargent automatiquement")
    print(" Attendez le message 'Modèles initialisés avec succès!'")
    
    print("\L'équipe peut maintenant:")
    print("Analyser des CV automatiquement")
    print("Calculer des scores de correspondance")
    print("Utiliser l'API REST")
    print("Tester l'interface web")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nEn cas de problème:")
        print("   1. Vérifiez votre connexion internet")
        print("   2. Assurez-vous d'avoir Python 3.8+")
        print("   3. Lancez en tant qu'administrateur si nécessaire")
        print("   4. Contactez l'équipe pour support")
        sys.exit(1)
