import torch
import re
import json
from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModel, pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Configuration GPU/CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Utilisation du device: {device}")

# Téléchargement des ressources NLTK nécessaires
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Téléchargement de 'punkt'...")
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Téléchargement de 'stopwords'...")
    nltk.download('stopwords')

def convert_numpy_types(obj):
    """Convertit récursivement les types NumPy/PyTorch en types Python natifs pour la sérialisation JSON"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif hasattr(obj, 'item'):  # Pour les tensors PyTorch
        return obj.item()
    else:
        return obj

# Classe danalyse de CV
class CVAnalyzer:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.sentence_model = None
        self.ner_pipeline = None
        self.device = self._get_device()
        self.skills_keywords = self._load_skills_keywords()
        self.experience_patterns = self._create_experience_patterns()
        self.education_patterns = self._create_education_patterns()
        
        self._initialize_models()
    
    def _get_device(self):
        """Détecte et configure l'utilisation du GPU si disponible"""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            print(f"🚀 GPU détecté: {torch.cuda.get_device_name(0)}")
            print(f"💾 Mémoire GPU disponible: {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB")
        else:
            device = torch.device('cpu')
            print("⚠️  GPU non disponible, utilisation du CPU")
        return device

# initialise les modeles NLP
    def _initialize_models(self):
        try:
            print(f"Chargement du modèle Sentence Transformer: {self.model_name} sur {self.device}")
            # Utiliser le device pour SentenceTransformer
            self.sentence_model = SentenceTransformer(self.model_name, device=self.device)
            
            print(f"Chargement du pipeline NER sur {self.device}...")
            # Utiliser le device pour le pipeline NER avec optimisations
            self.ner_pipeline = pipeline("ner", 
                                        model="dbmdz/bert-large-cased-finetuned-conll03-english",
                                        aggregation_strategy="simple",
                                        device=0 if self.device.type == 'cuda' else -1,  # 0 pour GPU, -1 pour CPU
                                        torch_dtype=torch.float16 if self.device.type == 'cuda' else torch.float32)  # Optimisation mémoire
            
            print("✅ Modèles initialisés avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation des modèles: {e}")
            # Fallback en CPU si GPU échoue
            if self.device.type == 'cuda':
                print("🔄 Tentative de chargement en mode CPU...")
                self.device = torch.device('cpu')
                try:
                    self.sentence_model = SentenceTransformer(self.model_name, device=self.device)
                    self.ner_pipeline = pipeline("ner", 
                                                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                                                aggregation_strategy="simple",
                                                device=-1)
                    print("✅ Modèles chargés en mode CPU!")
                except Exception as fallback_e:
                    print(f"❌ Échec total du chargement des modèles: {fallback_e}")
                    self.sentence_model = None
                    self.ner_pipeline = None
    
# charge les mots-clés de compétences par catégories
    def _load_skills_keywords(self) -> Dict[str, List[str]]:
        return {
            "programming": [
                "python", "java", "javascript", "c++", "c#", "php", "ruby", "go",
                "html", "css", "sql", "r", "matlab", "scala", "perl", "swift",
                "kotlin", "typescript", "dart", "rust"
            ],
            "frameworks": [
                "django", "flask", "react", "angular", "vue", "spring", "laravel",
                "express", "nodejs", "tensorflow", "pytorch", "scikit-learn",
                "pandas", "numpy", "bootstrap", "jquery"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
                "elasticsearch", "cassandra", "dynamodb"
            ],
            "tools": [
                "git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp",
                "linux", "unix", "windows", "macos", "jira", "confluence"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving",
                "analytical thinking", "creativity", "adaptability", "time management",
                "project management", "critical thinking"
            ],
            "languages": [
                "english", "french", "spanish", "german", "italian", "chinese",
                "japanese", "arabic", "portuguese", "russian"
            ]
        }
    
# patternes regex pour l'experience
    def _create_experience_patterns(self) -> List[str]:
        return [
            r'(\d+)\s*years?\s*of\s*experience',
            r'(\d+)\s*ans?\s*d[\'e]\s*expérience',
            r'experience:\s*(\d+)\s*years?',
            r'expérience:\s*(\d+)\s*ans?',
            r'(\d+)\+\s*years?',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?'
        ]

# patternes regex pour l'éducation
    def _create_education_patterns(self) -> List[str]:
        return [
            r'bachelor[\'s]?\s*(degree)?',
            r'master[\'s]?\s*(degree)?',
            r'phd|ph\.d|doctorate',
            r'mba',
            r'license|licence',
            r'ingénieur',
            r'university|université',
            r'college|école',
            r'certification|certificat'
        ]

# extrait les infos importantes d'un CV    
    def extract_text_from_cv(self, cv_text: str) -> Dict[str, any]:
        result = {
            'skills': self.extract_skills(cv_text),
            'experience': self.extract_experience(cv_text),
            'education': self.extract_education(cv_text),
            'languages': self.extract_languages(cv_text),
            'entities': self.extract_entities(cv_text),
            'summary': self.generate_summary(cv_text)
        }
        
        # Convertir tous les types NumPy/PyTorch en types Python natifs
        result = convert_numpy_types(result)
        
        return result

# extraire les compétences du texte
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills_list in self.skills_keywords.items():
            found_skills[category] = []
            for skill in skills_list:
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    found_skills[category].append(skill)
        
        found_skills = {k: v for k, v in found_skills.items() if v}
        
        return found_skills

# extrait les informations d'experience    
    def extract_experience(self, text: str) -> Dict[str, any]:
        experience_info = {
            'years_of_experience': 0,
            'job_titles': [],
            'companies': []
        }
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                years = [int(match) for match in matches if match.isdigit()]
                if years:
                    experience_info['years_of_experience'] = max(years)
                    break
        
        if self.ner_pipeline:
            entities = self.ner_pipeline(text)
            for entity in entities:
                if entity['entity_group'] == 'ORG':
                    experience_info['companies'].append(entity['word'])
        
        return experience_info

# extrait les informations d'éducation
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        education_list = []
        text_lower = text.lower()
        
        for pattern in self.education_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                education_list.append({
                    'type': match.group(),
                    'context': text[max(0, match.start()-50):match.end()+50]
                })
        
        return education_list

# extrait les informations de langues
    def extract_languages(self, text: str) -> List[str]:
        text_lower = text.lower()
        found_languages = []
        
        for language in self.skills_keywords['languages']:
            if re.search(r'\b' + re.escape(language.lower()) + r'\b', text_lower):
                found_languages.append(language)
        
        return found_languages

# extrait les entités nommées
    def extract_entities(self, text: str) -> List[Dict[str, any]]:
        if not self.ner_pipeline:
            return []
        
        try:
            entities = self.ner_pipeline(text)
            return entities
        except Exception as e:
            print(f"Erreur lors de l'extraction d'entités: {e}")
            return []

# genere un résumé du CV
    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        sentences = sent_tokenize(text)
        if len(sentences) <= max_sentences:
            return text
        
        return ' '.join(sentences[:max_sentences])

# calcule le score de correspondance entre un CV et une offre d'emploi
    def calculate_job_match_score(self, cv_text: str, job_description: str) -> Dict[str, float]:
        if not self.sentence_model:
            return {'error': 'Modèle non initialisé'}
        
        try:
            # Optimisation GPU : traitement par batch et gestion de la mémoire
            with torch.cuda.amp.autocast() if self.device.type == 'cuda' else torch.no_grad():
                # Encoder les textes avec optimisations
                cv_embedding = self.sentence_model.encode(
                    [cv_text], 
                    convert_to_tensor=True,
                    device=self.device,
                    show_progress_bar=False,
                    batch_size=1
                )
                job_embedding = self.sentence_model.encode(
                    [job_description], 
                    convert_to_tensor=True,
                    device=self.device,
                    show_progress_bar=False,
                    batch_size=1
                )
                
                # Calcul de similarité optimisé GPU
                similarity = torch.cosine_similarity(cv_embedding, job_embedding, dim=1)
                similarity_score = similarity.cpu().item()  # Ramener sur CPU pour le résultat
            
            cv_skills = self.extract_skills(cv_text)
            job_skills = self.extract_skills(job_description)
            
            skills_score = self._calculate_skills_match(cv_skills, job_skills)
            
            overall_score = (similarity_score * 0.6 + skills_score * 0.4) * 100
            
            result = {
                'overall_score': round(float(overall_score), 2),
                'semantic_similarity': round(float(similarity_score) * 100, 2),
                'skills_match_score': round(float(skills_score) * 100, 2),
                'cv_skills': cv_skills,
                'job_skills': job_skills
            }
            
            # Convertir tous les types NumPy en types Python natifs
            result = convert_numpy_types(result)
            
            return result
            
        except Exception as e:
            return {'error': f'Erreur lors du calcul: {e}'}

# calcule le score de correspondance des compétences
    def _calculate_skills_match(self, cv_skills: Dict, job_skills: Dict) -> float:
        if not cv_skills or not job_skills:
            return 0.0
        
        total_job_skills = sum(len(skills) for skills in job_skills.values())
        if total_job_skills == 0:
            return 0.0
        
        matched_skills = 0
        for category, job_skills_list in job_skills.items():
            cv_skills_list = cv_skills.get(category, [])
            for skill in job_skills_list:
                if skill in cv_skills_list:
                    matched_skills += 1
        
        return matched_skills / total_job_skills

    def calculate_overall_score(self, analysis_data: Dict) -> float:
        """
        Calcule un score global basé sur l'analyse du CV
        """
        try:
            skills = analysis_data.get('skills', {})
            experience = analysis_data.get('experience', {})
            text_length = analysis_data.get('text_length', 0)
            
            # Score basé sur les compétences (40% du total)
            skills_count = sum(len(skill_list) for skill_list in skills.values())
            skills_score = min(skills_count / 10, 1.0) * 40  # Max 40 points
            
            # Score basé sur l'expérience (35% du total)
            years_experience = experience.get('years_of_experience', 0)
            experience_score = min(years_experience / 10, 1.0) * 35  # Max 35 points
            
            # Score basé sur la qualité du CV (longueur du texte) (25% du total)
            text_quality_score = 0
            if text_length > 500:  # CV suffisamment détaillé
                text_quality_score = 25
            elif text_length > 200:
                text_quality_score = 15
            elif text_length > 100:
                text_quality_score = 10
            
            total_score = skills_score + experience_score + text_quality_score
            
            # S'assurer que le score est entre 0 et 100
            return round(min(max(total_score, 0), 100), 2)
            
        except Exception as e:
            print(f"Erreur lors du calcul du score global: {e}")
            return 50.0  # Score par défaut
    
    def cleanup_gpu_memory(self):
        """Nettoie la mémoire GPU pour éviter les fuites mémoire"""
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
            if torch.cuda.is_available():
                print(f"💾 Mémoire GPU libérée: {torch.cuda.memory_reserved(0) // 1024**2} MB utilisés")
    
    def get_gpu_info(self):
        """Retourne les informations sur l'utilisation du GPU"""
        if self.device.type == 'cuda':
            return {
                'gpu_available': True,
                'gpu_name': torch.cuda.get_device_name(0),
                'memory_allocated': torch.cuda.memory_allocated(0) // 1024**2,  # MB
                'memory_reserved': torch.cuda.memory_reserved(0) // 1024**2,    # MB
                'total_memory': torch.cuda.get_device_properties(0).total_memory // 1024**2  # MB
            }
        else:
            return {'gpu_available': False, 'using': 'CPU'}

if __name__ == "__main__":
    analyzer = CVAnalyzer()
    
    sample_cv = """
    John Doe
    Software Engineer
    5 years of experience in Python, Django, React
    Bachelor's degree in Computer Science
    Fluent in English and French
    """
    
    result = analyzer.extract_text_from_cv(sample_cv)
    print("Resultat de l'analyse:")
    print(json.dumps(result, indent=2))
