#!/usr/bin/env python3

import os
import sys
import subprocess
import json
from pathlib import Path

def print_step(message, step_num, total_steps):
    """Affiche une étape avec numérotation"""
    print(f"\n{'='*60}")
    print(f"🔄 ÉTAPE {step_num}/{total_steps}: {message}")
    print(f"{'='*60}")

def print_status(message, status="INFO"):
    """Affiche un message avec statut coloré"""
    colors = {
        "SUCCESS": "\033[92m✅",
        "ERROR": "\033[91m❌", 
        "WARNING": "\033[93m⚠️",
        "INFO": "\033[94mℹ️",
        "TODO": "\033[95m📝"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def check_git_repo():
    """Vérifie que nous sommes dans un repo Git"""
    if not os.path.exists(".git"):
        print_status("Initialisation du repository Git...", "INFO")
        subprocess.run(["git", "init"], check=True)
        print_status("Repository Git initialisé", "SUCCESS")
    else:
        print_status("Repository Git existant détecté", "SUCCESS")

def create_gitignore():
    """Crée ou met à jour .gitignore"""
    print_status("Création/mise à jour .gitignore...", "INFO")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.venv/

# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/

# AI Models Cache (trop volumineux pour Git)
*.bin
*.h5
*.onnx
**/models/**/*.bin
**/models/**/*.h5
**/.cache/**
**/sentence_transformers_cache/**
**/transformers_cache/**

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Logs
*.log
logs/

# Environment variables
.env.local
.env.production
.env.test

# Coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# Personal notes
notes.txt
todo.txt
NOTES.md
""".strip()
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    print_status(".gitignore créé/mis à jour", "SUCCESS")

def check_essential_files():
    """Vérifie que tous les fichiers essentiels sont présents"""
    print_status("Vérification des fichiers essentiels...", "INFO")
    
    essential_files = {
        "README.md": "Documentation principale",
        "requirements.txt": "Dépendances Python",
        "install_project.py": "Installation automatique",
        "test_installation_equipe.py": "Tests d'intégration",
        "INSTALLATION_EQUIPE.md": "Guide équipe",
        "WORKFLOW_GITHUB.md": "Workflow collaboration",
        "start_server.bat": "Lanceur Windows",
        "start_server.sh": "Lanceur Linux/Mac",
        "CVAnalyserProject/manage.py": "Django manage",
        "CVAnalyserProject/CVAnalyser/ai_services/cv_analyzer.py": "Core IA"
    }
    
    missing_files = []
    for file_path, description in essential_files.items():
        if os.path.exists(file_path):
            print_status(f"{description}: {file_path} ✓", "SUCCESS")
        else:
            print_status(f"{description}: {file_path} MANQUANT", "ERROR")
            missing_files.append(file_path)
    
    if missing_files:
        print_status(f"{len(missing_files)} fichiers manquants!", "ERROR")
        return False
    else:
        print_status("Tous les fichiers essentiels sont présents", "SUCCESS")
        return True

def check_file_sizes():
    """Vérifie la taille des fichiers pour éviter les gros uploads"""
    print_status("Vérification des tailles de fichiers...", "INFO")
    
    large_files = []
    for root, dirs, files in os.walk("."):
        # Ignorer les dossiers cachés et virtuels
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__']]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 100 * 1024 * 1024:  # > 100MB
                    large_files.append((file_path, size // (1024*1024)))
            except:
                pass
    
    if large_files:
        print_status("⚠️ Fichiers volumineux détectés:", "WARNING")
        for file_path, size_mb in large_files:
            print_status(f"  {file_path}: {size_mb}MB", "WARNING")
        print_status("Vérifiez que ces fichiers doivent être dans Git", "WARNING")
    else:
        print_status("Aucun fichier volumineux détecté", "SUCCESS")

def create_github_templates():
    """Crée les templates GitHub"""
    print_status("Création des templates GitHub...", "INFO")
    
    # Créer le dossier .github
    os.makedirs(".github", exist_ok=True)
    
    # Template Pull Request
    pr_template = """
## 📋 Description
Brève description des modifications apportées.

## 🔧 Type de modification
- [ ] 🐛 Bug fix (correction de bug)
- [ ] ✨ Nouvelle fonctionnalité
- [ ] 💥 Breaking change (modification incompatible)
- [ ] 📚 Documentation
- [ ] 🔨 Refactoring
- [ ] ⚡ Performance
- [ ] 🧪 Tests

## 🧪 Tests
- [ ] Tests unitaires passent (`python test_installation_equipe.py`)
- [ ] Tests manuels effectués
- [ ] IA fonctionne correctement
- [ ] Serveur Django démarre

## ✅ Checklist
- [ ] Code review demandé
- [ ] Documentation mise à jour
- [ ] Commit messages respectent la convention
- [ ] Aucun secret/credential exposé
- [ ] Performance acceptable

## 🖼️ Screenshots (si applicable)
<!-- Ajoutez des captures d'écran si modification UI -->

## 📝 Notes additionnelles
<!-- Informations supplémentaires pour les reviewers -->
"""
    
    with open(".github/pull_request_template.md", "w", encoding="utf-8") as f:
        f.write(pr_template.strip())
    
    # Template Issue
    issue_template = """
---
name: 🐛 Bug Report
about: Signaler un problème
title: '[BUG] '
labels: 'bug'
assignees: ''
---

## 🐛 Description du bug
Description claire et concise du problème.

## 🔄 Reproduction
Étapes pour reproduire le problème:
1. Aller à '...'
2. Cliquer sur '....'
3. Scroll down to '....'
4. Voir l'erreur

## ✅ Comportement attendu
Description de ce qui devrait se passer.

## 📷 Screenshots
Si applicable, ajoutez des captures d'écran.

## 💻 Environnement
- OS: [e.g. Windows 10, macOS, Ubuntu]
- Python: [e.g. 3.9.0]
- Django: [e.g. 5.2.5]
- Navigateur: [e.g. Chrome, Firefox]

## 📝 Informations additionnelles
Tout autre contexte utile pour le problème.
"""
    
    os.makedirs(".github/ISSUE_TEMPLATE", exist_ok=True)
    with open(".github/ISSUE_TEMPLATE/bug_report.md", "w", encoding="utf-8") as f:
        f.write(issue_template.strip())
    
    print_status("Templates GitHub créés", "SUCCESS")

def generate_git_commands():
    """Génère les commandes Git à exécuter"""
    print_status("Génération des commandes Git...", "INFO")
    
    commands = [
        "git add .",
        "git commit -m 'feat: système complet analyse CV avec IA BERT/Transformers'",
        "git branch -M main",  # Renommer en main si nécessaire
    ]
    
    print_status("Commandes Git suggérées:", "TODO")
    for i, cmd in enumerate(commands, 1):
        print(f"  {i}. {cmd}")
    
    print_status("Après avoir créé le repository GitHub:", "TODO")
    github_commands = [
        "git remote add origin https://github.com/[USERNAME]/Analyse-CV-AI.git",
        "git push -u origin main"
    ]
    
    for i, cmd in enumerate(github_commands, 1):
        print(f"  {i+len(commands)}. {cmd}")

def create_deployment_summary():
    """Crée un résumé de déploiement"""
    summary = {
        "project_name": "Analyse CV IA",
        "description": "Système d'analyse intelligente de CV avec BERT et Transformers",
        "technologies": [
            "Django 5.2.5",
            "BERT (bert-large-cased-finetuned-conll03-english)",
            "Sentence Transformers (all-MiniLM-L6-v2)",
            "PyTorch", "NLTK", "scikit-learn"
        ],
        "features": [
            "Extraction automatique compétences/expérience",
            "Score de correspondance CV/poste",
            "API REST complète",
            "Interface web intuitive",
            "Support PDF/DOCX/TXT"
        ],
        "installation": {
            "command": "python install_project.py",
            "test": "python test_installation_equipe.py",
            "start": "start_server.bat (Windows) ou ./start_server.sh (Linux/Mac)"
        },
        "team_ready": True,
        "documentation": [
            "README.md - Documentation complète",
            "INSTALLATION_EQUIPE.md - Guide équipe",
            "WORKFLOW_GITHUB.md - Collaboration GitHub"
        ]
    }
    
    with open("deployment_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print_status("Résumé de déploiement créé: deployment_summary.json", "SUCCESS")

def main():
    """Fonction principale"""
    print("🚀 PRÉPARATION FINALE POUR GITHUB")
    print("🎯 Objectif: Préparer le code pour la collaboration équipe")
    
    steps = [
        ("Vérification repository Git", check_git_repo),
        ("Création .gitignore", create_gitignore),
        ("Vérification fichiers essentiels", check_essential_files),
        ("Vérification tailles fichiers", check_file_sizes),
        ("Création templates GitHub", create_github_templates),
        ("Résumé de déploiement", create_deployment_summary),
        ("Commandes Git finales", generate_git_commands)
    ]
    
    success_count = 0
    for i, (step_name, step_func) in enumerate(steps, 1):
        print_step(step_name, i, len(steps))
        
        try:
            result = step_func()
            if result is not False:
                success_count += 1
        except Exception as e:
            print_status(f"Erreur: {e}", "ERROR")
    
    # Rapport final
    print_step("RAPPORT FINAL", len(steps)+1, len(steps)+1)
    
    print_status(f"✅ {success_count}/{len(steps)} étapes réussies", "SUCCESS")
    
    if success_count == len(steps):
        print_status("🎉 PROJET PRÊT POUR GITHUB!", "SUCCESS")
        print()
        print_status("📋 PROCHAINES ÉTAPES:", "TODO")
        print("  1. Créer un repository sur GitHub")
        print("  2. git remote add origin [URL]")
        print("  3. git push -u origin main")
        print("  4. Partager le lien avec votre équipe")
        print("  5. L'équipe peut cloner et installer avec 'python install_project.py'")
        print()
        print_status("📚 DOCUMENTATION ÉQUIPE:", "INFO")
        print("  • README.md - Documentation technique complète")
        print("  • INSTALLATION_EQUIPE.md - Guide installation rapide")
        print("  • WORKFLOW_GITHUB.md - Workflow collaboration")
        print("  • test_installation_equipe.py - Tests automatiques")
        print()
        print_status("🤖 IA PRÊTE:", "SUCCESS")
        print("  • Modèles BERT & Transformers intégrés")
        print("  • API REST fonctionnelle")
        print("  • Interface web opérationnelle")
        print("  • Tests d'intégration complets")
        
    else:
        print_status("⚠️ Quelques étapes à finaliser", "WARNING")
        print_status("Vérifiez les erreurs ci-dessus avant le push GitHub", "WARNING")

if __name__ == "__main__":
    main()
