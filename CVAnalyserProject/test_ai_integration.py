import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVAnalyserProject.settings')
django.setup()

from CVAnalyser.ai_services.dataset_manager import DatasetManager
from CVAnalyser.ai_services.cv_analyzer import CVAnalyzer
from CVAnalyser.ai_services.text_extractor import TextExtractor

def test_dataset_download():
    print("=== TEST TÉLÉCHARGEMENT DATASET ===")
    
    try:
        manager = DatasetManager()
        
        print("Téléchargement du dataset en cours...")
        path = manager.download_kaggle_dataset()
        
        if path:
            print(f"Dataset téléchargé avec succès dans: {path}")
            
            # Explorer le dataset
            print("\nExploration du dataset...")
            df = manager.load_and_explore_dataset()
            
            if df is not None:
                print(f"Dataset chargé: {len(df)} lignes, {len(df.columns)} colonnes")
                print(f"Colonnes: {list(df.columns)}")
                
                # Préprocesser
                print("\nPréprocessing du dataset...")
                processed_df = manager.preprocess_dataset()
                
                if processed_df is not None:
                    print("Préprocessing terminé avec succès")
                    return True
            
        else:
            print("Erreur lors du téléchargement")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_cv_analyzer():
    """Test l'analyseur de CV"""
    print("\n=== TEST ANALYSEUR CV ===")
    
    try:
        # Initialiser l'analyseur
        print("Initialisation de l'analyseur IA...")
        analyzer = CVAnalyzer()
        
        # CV de test
        sample_cv = """
        Jean Dupont
        Ingénieur Logiciel Senior
        Email: jean.dupont@example.com
        Téléphone: 01 23 45 67 89
        
        EXPÉRIENCE PROFESSIONNELLE:
        
        Développeur Senior - TechCorp (2020-2024)
        • 4 années d'expérience en développement Python
        • Expertise en Django et FastAPI
        • Développement d'applications web avec React
        • Gestion d'équipe de 5 développeurs
        • Méthodologies Agile et Scrum
        
        Développeur Junior - StartupXYZ (2018-2020)
        • 2 ans d'expérience en JavaScript et Node.js
        • Développement d'APIs REST
        • Travail avec MongoDB et PostgreSQL
        
        FORMATION:
        • Master en Informatique - École Centrale (2018)
        • Licence en Mathématiques - Université Paris (2016)
        
        COMPÉTENCES TECHNIQUES:
        • Langages: Python, JavaScript, Java, SQL
        • Frameworks: Django, React, Vue.js, Express
        • Bases de données: PostgreSQL, MongoDB, Redis
        • Outils: Git, Docker, Kubernetes, AWS
        • Méthodologies: Agile, Scrum, DevOps
        
        LANGUES:
        • Français (natif)
        • Anglais (courant)
        • Espagnol (notions)
        
        CERTIFICATIONS:
        • AWS Certified Developer
        • Scrum Master Certified
        """
        
        print("Analyse du CV en cours...")
        result = analyzer.extract_text_from_cv(sample_cv)
        
        print("✅ Analyse terminée!")
        print(f"Compétences détectées: {result['skills']}")
        print(f"Expérience: {result['experience']}")
        print(f"Formation: {result['education']}")
        print(f"Langues: {result['languages']}")
        
        job_description = """
        Poste: Développeur Python Senior
        
        Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe.
        
        Compétences requises:
        • 3+ années d'expérience en Python
        • Maîtrise de Django
        • Expérience avec React
        • Connaissance des bases de données PostgreSQL
        • Expérience avec AWS
        • Méthodologies Agile
        
        Compétences appréciées:
        • Docker et Kubernetes
        • Leadership d'équipe
        • Anglais courant
        """
        
        print("\nCalcul de correspondance avec le poste...")
        match_result = analyzer.calculate_job_match_score(sample_cv, job_description)
        
        print("✅ Correspondance calculée!")
        print(f"Score global: {match_result['overall_score']}%")
        print(f"Similarité sémantique: {match_result['semantic_similarity']}%")
        print(f"Correspondance compétences: {match_result['skills_match_score']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return False

def test_text_extractor():
    """Test l'extracteur de texte"""
    print("\n=== TEST EXTRACTEUR TEXTE ===")
    
    try:
        test_content = """
        CV Test
        Nom: Marie Martin
        Poste: Data Scientist
        
        Expérience:
        • 3 ans en analyse de données
        • Python, R, SQL
        • Machine Learning avec scikit-learn
        • Visualisation avec matplotlib et seaborn
        
        Formation:
        • Master en Data Science
        • Licence en Mathématiques
        """
        
        test_file = "test_cv.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"Extraction du texte de {test_file}...")
        result = TextExtractor.extract_and_clean(test_file)
        
        if result['success']:
            print("Extraction réussie!")
            print(f"Texte extrait: {result['cleaned_text'][:100]}...")
        else:
            print(f"Erreur: {result['error']}")
            
        # Nettoyer
        os.remove(test_file)
        return result['success']
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("DÉBUT DES TESTS D'INTÉGRATION IA")
    print("=" * 50)
    
    results = []
    
    results.append(test_dataset_download())
    
    results.append(test_cv_analyzer())
    
    results.append(test_text_extractor())
    
    print("\n" + "=" * 50)
    print("RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    results = [r for r in results if r is not None]
    success_count = sum(1 for r in results if r is True)
    total_tests = len(results)
    
    test_names = [
        "Téléchargement dataset",
        "Analyseur CV",
        "Extracteur texte"
    ]
    
    for i, name in enumerate(test_names):
        if i < len(results):
            success = results[i]
            status = "RÉUSSI" if success else "ÉCHEC"
        else:
            status = "NON TESTÉ"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\nRésultat global: {success_count}/{len(test_names)} tests réussis")
    
    if success_count >= 2:
        print("\n🎉 L'intégration IA est fonctionnelle!")
        print("\nPour utiliser l'API:")
        print("1. Lancez le serveur Django: python manage.py runserver")
        print("2. Testez l'endpoint /api/ai-status/ pour vérifier le statut")
        print("3. Utilisez /api/upload-cv/ pour analyser des CV")
    else:
        print("\nCertains tests ont échoué. L'IA de base est disponible.")
        print("   Le système peut fonctionner avec des fonctionnalités limitées.")

if __name__ == "__main__":
    main()
