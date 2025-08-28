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

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Classe danalyse de CV
class CVAnalyzer:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.sentence_model = None
        self.ner_pipeline = None
        self.skills_keywords = self._load_skills_keywords()
        self.experience_patterns = self._create_experience_patterns()
        self.education_patterns = self._create_education_patterns()
        
        self._initialize_models()
    
# initialise les modeles NLP
    def _initialize_models(self):
        try:
            print(f"Chargement du modèle Sentence Transformer: {self.model_name}")
            self.sentence_model = SentenceTransformer(self.model_name)
            
            print("Chargement du pipeline NER...")
            self.ner_pipeline = pipeline("ner", 
                                        model="dbmdz/bert-large-cased-finetuned-conll03-english",
                                        aggregation_strategy="simple")
            
            print("Modèles initialisés avec succès!")
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation des modèles: {e}")
    
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
            cv_embedding = self.sentence_model.encode([cv_text])
            job_embedding = self.sentence_model.encode([job_description])
            
            similarity = cosine_similarity(cv_embedding, job_embedding)[0][0]
            
            cv_skills = self.extract_skills(cv_text)
            job_skills = self.extract_skills(job_description)
            
            skills_score = self._calculate_skills_match(cv_skills, job_skills)
            
            overall_score = (similarity * 0.6 + skills_score * 0.4) * 100
            
            return {
                'overall_score': round(overall_score, 2),
                'semantic_similarity': round(similarity * 100, 2),
                'skills_match_score': round(skills_score * 100, 2),
                'cv_skills': cv_skills,
                'job_skills': job_skills
            }
            
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
