"""
Script de configuration et test du projet Django avec IA
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    print(f"Commande: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print("✅ Sortie:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur:")
        print(e.stderr if e.stderr else e.stdout)
        return False

def setup_django_project():
    """Configure le projet Django"""
    print("🚀 Configuration du projet Django avec IA")
    
    # Changer vers le répertoire du projet
    os.chdir("CVAnalyserProject")
    
    # 1. Créer les migrations
    if not run_command("python manage.py makemigrations", "Création des migrations"):
        return False
    
    # 2. Appliquer les migrations
    if not run_command("python manage.py migrate", "Application des migrations"):
        return False
    
    # 3. Créer les dossiers nécessaires
    print("\n📁 Création des dossiers...")
    folders = ["media", "media/resumes", "ai_models", "datasets"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"✅ Dossier créé: {folder}")
    
    return True

def test_ai_components():
    """Teste les composants IA"""
    print("\n🤖 Test des composants IA")
    
    if not run_command("python test_ai_integration.py", "Test de l'intégration IA"):
        print("⚠️  Certains tests peuvent échouer la première fois (téléchargement des modèles)")
        return False
    
    return True

def create_superuser():
    """Propose de créer un superutilisateur"""
    print("\n👤 Création d'un superutilisateur Django")
    response = input("Voulez-vous créer un superutilisateur maintenant ? (y/n): ")
    
    if response.lower() == 'y':
        run_command("python manage.py createsuperuser", "Création du superutilisateur")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🎯 CONFIGURATION DJANGO + IA POUR ANALYSE DE CV")
    print("=" * 60)
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists("manage.py"):
        if os.path.exists("CVAnalyserProject/manage.py"):
            os.chdir("CVAnalyserProject")
        else:
            print("❌ Erreur: manage.py non trouvé. Assurez-vous d'être dans le bon répertoire.")
            return
    
    # Configuration Django
    if not setup_django_project():
        print("❌ Erreur lors de la configuration Django")
        return
    
    # Test des composants IA
    print("\n🔍 Test des composants IA (optionnel)")
    test_choice = input("Voulez-vous tester l'IA maintenant ? (y/n): ")
    if test_choice.lower() == 'y':
        test_ai_components()
    
    # Création superutilisateur
    create_superuser()
    
    # Instructions finales
    print("\n" + "=" * 60)
    print("🎉 CONFIGURATION TERMINÉE!")
    print("=" * 60)
    print("\n📋 Instructions pour utiliser le système:")
    print("\n1. Démarrer le serveur Django:")
    print("   python manage.py runserver")
    print("\n2. Ouvrir le navigateur sur:")
    print("   http://127.0.0.1:8000/")
    print("\n3. Tester l'interface web pour:")
    print("   • Vérifier le statut de l'IA")
    print("   • Télécharger le dataset Kaggle")
    print("   • Analyser des CV")
    print("   • Calculer des correspondances avec des postes")
    print("\n4. API Endpoints disponibles:")
    print("   • GET  /api/ai-status/         - Statut de l'IA")
    print("   • POST /api/upload-cv/         - Upload et analyse CV")
    print("   • POST /api/analyze-cv-job/    - Correspondance CV/poste")
    print("   • GET  /api/resumes/           - Liste des CV")
    print("   • POST /api/download-dataset/  - Télécharger dataset")
    print("\n5. Interface d'administration:")
    print("   http://127.0.0.1:8000/admin/")
    print("\n🔧 Fonctionnalités IA intégrées:")
    print("   ✅ Extraction de texte (PDF, DOCX, TXT)")
    print("   ✅ Analyse NLP avec modèles pré-entraînés")
    print("   ✅ Extraction de compétences, expérience, formation")
    print("   ✅ Calcul de scores de correspondance")
    print("   ✅ Reconnaissance d'entités nommées")
    print("   ✅ Similarité sémantique avec Sentence Transformers")
    
    print(f"\n📁 Répertoire de travail: {os.getcwd()}")

if __name__ == "__main__":
    main()
