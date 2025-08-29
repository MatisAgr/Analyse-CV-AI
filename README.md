# Analyse CV IA

Système d'analyse intelligente de CV avec modèles BERT et Transformers.

## Installation rapide
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement
```bash
cd CVAnalyzerProject
python manage.py runserver
```

Interface web : http://127.0.0.1:8000/

## Fonctionnalités
- Extraction automatique compétences/expérience
- Analyse IA avec BERT
- Score de correspondance CV/poste
- API REST
- Interface web

## Technologies
- Django 5.2.5
- BERT (bert-large-cased-finetuned-conll03-english)
- Sentence Transformers (all-MiniLM-L6-v2)
- PyTorch, NLTK, scikit-learn
