# 🤖 Django Analyseur de CV avec IA

> **Système intelligent d'analyse de CV utilisant BERT et Sentence Transformers**

## 🎯 Vue d'ensemble

Projet Django d'analyse automatique de CV avec Intelligence Artificielle. Le système extrait automatiquement les compétences, l'expérience et calcule des scores de correspondance avec des postes.

### 🚀 Fonctionnalités principales
- ✅ **Analyse automatique** de CV (PDF, DOCX, TXT)
- ✅ **Extraction de compétences** par catégories
- ✅ **Détection d'expérience** et formation
- ✅ **Score de correspondance** CV/poste avec IA
- ✅ **API REST complète** pour intégration
- ✅ **Interface web** de test et démonstration

## 🏃‍♂️ Installation rapide (pour l'équipe)

### **Option 1: Installation automatique (Recommandée)**

```bash
# 1. Cloner le projet
git clone <votre-repo-github>
cd Analyse-CV-AI

# 2. Installation automatique (tout en une fois)
python install_project.py

# 3. Démarrer le serveur
# Windows: double-clic sur start_server.bat
# Linux/Mac: ./start_server.sh
```

### **Option 2: Installation manuelle**

```bash
# 1. Créer l'environnement virtuel
python -m venv .venv

# 2. Activer l'environnement
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration Django
cd CVAnalyserProject
python manage.py makemigrations
python manage.py migrate

# 5. Démarrer le serveur
python manage.py runserver
```

## 🌐 Utilisation

### **Interface Web**
- Ouvrez: http://127.0.0.1:8000/
- Testez l'IA avec le bouton "Tester l'IA"
- Uploadez des CV pour analyse automatique
- Calculez des correspondances avec des postes

### **API REST**

#### Vérifier le statut IA
```bash
curl http://127.0.0.1:8000/api/ai-status/
```

#### Analyser un CV
```bash
curl -X POST http://127.0.0.1:8000/api/upload-cv/ \
  -F "cv_file=@mon_cv.pdf" \
  -F "name=Jean Dupont" \
  -F "email=jean@example.com"
```

#### Calculer une correspondance
```bash
curl -X POST http://127.0.0.1:8000/api/analyze-cv-job/ \
  -H "Content-Type: application/json" \
  -d '{"resume_id": 1, "job_description": "Recherche développeur Python..."}'
```

## � Modèles IA utilisés

- **Sentence Transformers** (`all-MiniLM-L6-v2`) - Similarité sémantique
- **BERT NER** (`bert-large-cased-finetuned-conll03-english`) - Entités nommées
- **NLTK** - Traitement du langage naturel

> ⚠️ **Premier lancement**: Les modèles (1.4GB) se téléchargent automatiquement. Attendez 1-2 minutes.

## 📁 Structure du projet

```
├── CVAnalyserProject/           # Projet Django principal
│   ├── CVAnalyser/             # App Django avec IA
│   │   ├── ai_services/        # Services IA
│   │   │   ├── cv_analyzer.py      # 🧠 Analyseur principal
│   │   │   ├── text_extractor.py   # 📄 Extraction PDF/DOCX
│   │   │   └── dataset_manager.py  # 📊 Gestion datasets
│   │   ├── models.py           # Modèles Django
│   │   ├── views.py            # API avec IA
│   │   └── templates/          # Interface web
│   └── manage.py
├── requirements.txt            # Dépendances Python
├── install_project.py          # 🚀 Installation auto
└── README.md                   # Cette documentation
```

## 🧪 Tests

### Test complet du système
```bash
cd CVAnalyserProject
python test_ai_integration.py
```

### Test de l'API
```bash
python demo_api.py
```

## 🔧 Configuration

### Personnaliser les compétences
Modifiez `CVAnalyser/ai_services/cv_analyzer.py` → `_load_skills_keywords()`

### Changer de modèle IA
Modifiez `CVAnalyserProject/settings.py` → `NLP_MODEL_NAME`

### Formats de fichiers supportés
Modifiez `CVAnalyserProject/settings.py` → `ALLOWED_CV_EXTENSIONS`

## 📊 Exemple d'utilisation

### CV d'exemple à tester
```text
Marie Dubois - Développeuse Full Stack

EXPÉRIENCE:
• 5 ans d'expérience en Python et Django
• Développement Frontend avec React
• Bases de données PostgreSQL et MongoDB

COMPÉTENCES:
Python, Django, React, JavaScript, SQL, Docker, Git

FORMATION:
Master en Informatique (2019)

LANGUES:
Français (natif), Anglais (courant)
```

### Résultat d'analyse automatique
```json
{
  "skills": {
    "programming": ["python", "javascript"],
    "frameworks": ["django", "react"],
    "databases": ["postgresql", "mongodb"],
    "tools": ["docker", "git"]
  },
  "experience": {
    "years_of_experience": 5
  },
  "languages": ["français", "anglais"]
}
```

## 🚨 Dépannage

### Erreurs communes

**❌ "Modèles non chargés"**
- Attendez 1-2 minutes au premier lancement
- Vérifiez votre connexion internet
- Vérifiez `/api/ai-status/`

**❌ "Erreur d'import transformers"**
```bash
pip install --upgrade transformers torch
```

**❌ "Erreur PDF/DOCX"**
```bash
pip install --upgrade PyPDF2 python-docx
```

### Support
- Vérifiez les logs Django pour les erreurs détaillées
- Testez `/api/ai-status/` pour diagnostiquer l'IA
- Utilisez `DEBUG=True` en développement

## 🏢 Cas d'usage métier

### Pour les RH
- Tri automatique de candidatures
- Scoring objectif des profils
- Correspondance précise avec les postes
- Gain de temps considérable

### Pour les développeurs
- API REST prête à l'emploi
- Intégration facile dans vos apps
- Modèles IA pré-configurés
- Documentation complète

## 🚀 Déploiement production

### Docker (Recommandé)
```dockerfile
FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "CVAnalyserProject/manage.py", "runserver", "0.0.0.0:8000"]
```

### Variables d'environnement
```bash
export DEBUG=False
export SECRET_KEY="votre-clé-secrète"
export ALLOWED_HOSTS="votre-domaine.com"
```

## 📈 Roadmap

### Version actuelle (v1.0)
- ✅ Analyse CV avec IA
- ✅ Interface web
- ✅ API REST
- ✅ Modèles pré-entraînés

### Prochaines versions
- [ ] Tableau de bord avancé
- [ ] Fine-tuning des modèles
- [ ] Intégration Outlook/Gmail
- [ ] Export PDF des analyses
- [ ] Authentification utilisateurs

## 📄 Licence

MIT License - Voir LICENSE pour plus de détails

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche: `git checkout -b feature/nouvelle-fonctionnalite`
3. Commitez: `git commit -m 'Ajout nouvelle fonctionnalité'`
4. Push: `git push origin feature/nouvelle-fonctionnalite`
5. Ouvrez une Pull Request

## � Support équipe

**🎯 Contacts:**
- **Lead IA**: [Votre nom] - Questions sur l'IA et modèles
- **Backend**: [Nom] - Questions Django et API
- **Frontend**: [Nom] - Questions interface web

**🔗 Ressources:**
- Documentation Django: https://docs.djangoproject.com/
- Hugging Face Transformers: https://huggingface.co/docs/transformers/
- Sentence Transformers: https://www.sbert.net/

---

## ✨ Développé avec ❤️ pour l'analyse intelligente de CV

**🎉 Prêt à analyser des milliers de CV automatiquement !**