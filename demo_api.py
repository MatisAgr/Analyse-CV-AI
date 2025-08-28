import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_ai_status():
    """Test le statut de l'IA"""
    print("Test du statut IA...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai-status/")
        data = response.json()
        
        if data.get('success'):
            print("IA opérationnelle!")
            print(f"   Modèles chargés: {data.get('ai_models_loaded')}")
            print(f"   Pipeline NER: {data.get('ner_pipeline_loaded')}")
        else:
            print(f"Erreur IA: {data.get('error')}")
        
        return data.get('success', False)
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return False

def create_test_cv_file():
    """Crée un fichier CV de test"""
    cv_content = """
MARIE DUBOIS
Développeuse Full Stack Senior

📧 marie.dubois@email.com
📱 +33 6 12 34 56 78
🌐 LinkedIn: linkedin.com/in/mariedubois

RÉSUMÉ PROFESSIONNEL
Développeuse passionnée avec 6 ans d'expérience dans le développement d'applications web modernes.
Expertise en Python/Django et React. Forte capacité d'adaptation et excellent esprit d'équipe.

EXPÉRIENCE PROFESSIONNELLE

Développeuse Senior | TechInnovate (2021-2024)
• Lead technique sur 3 projets web avec Django et React
• Encadrement d'une équipe de 4 développeurs juniors
• Mise en place d'architectures microservices avec Docker
• Amélioration des performances des applications de 40%

Développeuse Full Stack | WebSolutions (2019-2021)
• Développement d'applications SaaS avec Django REST Framework
• Frontend React avec TypeScript et Redux
• Intégration de systèmes de paiement (Stripe, PayPal)
• Mise en place de tests automatisés (Jest, Pytest)

Développeuse Junior | StartupXYZ (2018-2019)
• Première expérience en développement web
• Apprentissage des bonnes pratiques de développement
• Participation à tous les aspects du cycle de développement

FORMATION
Master en Informatique | École Centrale Paris (2018)
Licence en Mathématiques | Université Paris-Saclay (2016)

COMPÉTENCES TECHNIQUES

Langages de programmation:
• Python (expert) - 6 ans
• JavaScript/TypeScript (avancé) - 5 ans
• Java (intermédiaire) - 2 ans
• SQL (avancé) - 5 ans

Frameworks & Technologies:
• Django, Django REST Framework
• React, Vue.js, Angular
• Node.js, Express
• PostgreSQL, MongoDB, Redis
• Docker, Kubernetes
• AWS, Azure
• Git, Jenkins, CI/CD

Méthodologies:
• Agile, Scrum
• Test-Driven Development
• DevOps practices
• Code review

COMPÉTENCES TRANSVERSALES
• Leadership technique
• Mentorat et formation
• Gestion de projet
• Communication technique
• Résolution de problèmes complexes

LANGUES
• Français (natif)
• Anglais (courant) - TOEIC 950
• Espagnol (notions)

CERTIFICATIONS
• AWS Certified Developer Associate (2023)
• Certified Scrum Master (2022)
• Python Institute PCAP (2021)

PROJETS PERSONNELS
• Contributrice open source sur Django (50+ commits)
• Blog technique avec 10k+ lecteurs mensuels
• Application mobile de gestion de budget (React Native)

CENTRES D'INTÉRÊT
• Veille technologique
• Randonnée et photographie
• Bénévolat dans l'enseignement du code
"""
    
    filename = "cv_test_marie_dubois.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(cv_content)
    
    return filename

def test_cv_upload_and_analysis():
    print("\nTest d'upload et d'analyse de CV...")
    
    try:
        cv_file = create_test_cv_file()
        
        with open(cv_file, 'rb') as f:
            files = {'cv_file': f}
            data = {
                'name': 'Marie Dubois',
                'email': 'marie.dubois@test.com'
            }
            
            response = requests.post(f"{BASE_URL}/api/upload-cv/", files=files, data=data)
        
        import os
        os.remove(cv_file)
        
        if response.status_code == 200:
            result = response.json()
            print("CV analysé avec succès!")
            print(f"   ID du CV: {result.get('resume_id')}")
            
            analysis = result.get('analysis', {})
            skills = analysis.get('skills', {})
            
            print("\nCompétences détectées:")
            for category, skill_list in skills.items():
                if skill_list:
                    print(f"   {category.upper()}: {', '.join(skill_list[:5])}...")
            
            experience = analysis.get('experience', {})
            print(f"\nExpérience: {experience.get('years_of_experience', 'Non détecté')} ans")
            
            languages = analysis.get('languages', [])
            if languages:
                print(f"Langues: {', '.join(languages)}")
            
            return result.get('resume_id')
        else:
            print(f"Erreur upload: {response.text}")
            return None
            
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def test_job_matching(resume_id):
    print("\nTest de correspondance avec un poste...")
    
    job_description = """
POSTE: Développeur Python Senior

DESCRIPTION:
Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe technique.
Vous travaillerez sur des projets innovants utilisant Django et des technologies modernes.

COMPÉTENCES REQUISES:
• 4+ années d'expérience en Python
• Maîtrise de Django et Django REST Framework
• Expérience avec React ou Vue.js
• Connaissance des bases de données PostgreSQL
• Expérience avec Docker et Kubernetes
• Méthodologies Agile/Scrum
• Bon niveau d'anglais

COMPÉTENCES APPRÉCIÉES:
• Expérience AWS ou Azure
• Leadership technique
• Contribution à l'open source
• Expérience en mentorat

AVANTAGES:
• Télétravail hybride
• Formation continue
• Équipe technique passionnée
• Projets à fort impact
"""
    
    try:
        data = {
            'resume_id': resume_id,
            'job_description': job_description
        }
        
        response = requests.post(
            f"{BASE_URL}/api/analyze-cv-job/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            match_result = result.get('match_result', {})
            
            print("Correspondance calculée!")
            print(f"   Score global: {match_result.get('overall_score', 0):.1f}%")
            print(f"   Similarité sémantique: {match_result.get('semantic_similarity', 0):.1f}%")
            print(f"   Correspondance compétences: {match_result.get('skills_match_score', 0):.1f}%")
            
            return True
        else:
            print(f"Erreur correspondance: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    print("DÉMONSTRATION DE L'API DJANGO + IA")
    print("=" * 50)
    
    print("Vérification de la connexion au serveur...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("Serveur Django accessible!")
        else:
            print(f"Serveur répond avec code: {response.status_code}")
    except Exception as e:
        print(f"Serveur non accessible: {e}")
        print("   Assurez-vous que le serveur Django est lancé avec:")
        print("   python manage.py runserver")
        return
    
    if not test_ai_status():
        print("IA non disponible - la démonstration continue avec des fonctionnalités limitées")
    
    resume_id = test_cv_upload_and_analysis()
    
    if not resume_id:
        print("Impossible de continuer sans CV analysé")
        return
    
    test_job_matching(resume_id)
    
    print("\n" + "=" * 50)
    print("DÉMONSTRATION TERMINÉE!")
    print("=" * 50)
    print("\nFonctionnalités démontrées:")
    print("Serveur Django avec IA intégrée")
    print("Upload et analyse automatique de CV")
    print("Extraction de compétences et expérience")
    print("Calcul de correspondance CV/poste")
    print("API REST complète")
    
    print(f"\nInterface web disponible sur: {BASE_URL}")
    print("\nEndpoints API testés:")
    print(f"• GET  {BASE_URL}/api/ai-status/")
    print(f"• POST {BASE_URL}/api/upload-cv/")
    print(f"• POST {BASE_URL}/api/analyze-cv-job/")
    
    print("\n🔧 Prochaines étapes:")
    print("• Tester l'interface web dans le navigateur")
    print("• Uploader vos propres CV pour analyse")
    print("• Intégrer l'API dans votre application")
    print("• Personnaliser les compétences et modèles IA")

if __name__ == "__main__":
    main()
