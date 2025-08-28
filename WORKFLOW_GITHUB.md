# 🔄 WORKFLOW GITHUB POUR L'ÉQUIPE

## 📥 Première récupération du code

### **Étape 1: Clone du repository**
```bash
git clone https://github.com/[votre-username]/Analyse-CV-AI.git
cd Analyse-CV-AI
```

### **Étape 2: Installation automatique**
```bash
# Installation complète en une commande
python install_project.py

# Test de l'installation
python test_installation_equipe.py
```

### **Étape 3: Premier lancement**
```bash
# Windows
start_server.bat

# Linux/Mac  
./start_server.sh
```

## 🌿 Workflow de développement

### **Structure des branches**
```
main/master          ← Production (protégée)
├── develop          ← Intégration équipe
├── feature/ai-bert  ← Nouvelles fonctionnalités IA
├── feature/ui-web   ← Interface utilisateur
├── hotfix/bug-cv    ← Corrections urgentes
└── docs/readme      ← Documentation
```

### **Workflow standard**
```bash
# 1. Récupérer les dernières modifications
git checkout develop
git pull origin develop

# 2. Créer une branche feature
git checkout -b feature/nom-fonctionnalite

# 3. Développer et tester
# ... modifications ...
python test_installation_equipe.py  # Tester avant commit

# 4. Commit et push
git add .
git commit -m "feat: ajout analyse sentiment CV"
git push origin feature/nom-fonctionnalite

# 5. Créer une Pull Request vers develop
```

## 👥 Rôles et responsabilités

### **🤖 Lead IA (vous)**
- **Branches**: `feature/ai-*`, `develop`
- **Responsabilités**:
  - Intégration nouveaux modèles
  - Optimisation performances IA
  - Review code IA de l'équipe
  - Maintenance `cv_analyzer.py`

```bash
# Workflow Lead IA
git checkout develop
git checkout -b feature/ai-sentiment-analysis
# ... développement ...
python test_installation_equipe.py
git commit -m "feat: ajout analyse sentiment dans CV"
```

### **🌐 Développeur Backend**
- **Branches**: `feature/api-*`, `feature/db-*`
- **Responsabilités**:
  - API Django endpoints
  - Modèles de données
  - Intégration IA/API
  - Performance base de données

```bash
# Workflow Backend
git checkout develop  
git checkout -b feature/api-bulk-analysis
# ... développement endpoints ...
```

### **🎨 Développeur Frontend**
- **Branches**: `feature/ui-*`, `feature/web-*`
- **Responsabilités**:
  - Interface web
  - Templates Django
  - UX/UI analyse CV
  - Tests utilisateur

```bash
# Workflow Frontend
git checkout develop
git checkout -b feature/ui-dashboard
# ... développement interface ...
```

### **🧪 QA/Testeur**
- **Branches**: `feature/test-*`, `hotfix/*`
- **Responsabilités**:
  - Tests d'intégration
  - Validation IA
  - Rapports de bugs
  - Tests de charge

```bash
# Workflow QA
git checkout develop
python test_installation_equipe.py  # Test complet
# Rapport de bugs...
```

## 🔒 Règles de collaboration

### **Protection des branches**
- ✅ `main/master`: **Merge uniquement via PR**
- ✅ `develop`: **Review obligatoire** 
- ✅ Tests automatiques avant merge
- ❌ Push direct interdit sur `main`

### **Convention de commits**
```bash
# Types de commits
feat: nouvelle fonctionnalité
fix: correction de bug  
docs: documentation
style: formatage code
refactor: refactoring
test: ajout tests
chore: maintenance

# Exemples
git commit -m "feat: ajout extraction compétences BERT"
git commit -m "fix: correction timeout modèles IA"
git commit -m "docs: mise à jour README installation"
```

### **Pull Request checklist**
- [ ] ✅ Tests passent (`python test_installation_equipe.py`)
- [ ] 📝 Description claire des modifications
- [ ] 🧪 Code testé localement
- [ ] 📚 Documentation mise à jour si nécessaire
- [ ] 🔍 Review code demandée
- [ ] 🏷️ Labels appropriés (AI, Backend, Frontend, etc.)

## 🚀 Déploiement et releases

### **Cycle de release**
```bash
# 1. Merge develop → main
git checkout main
git merge develop
git tag -a v1.0.0 -m "Release v1.0.0: Analyse CV IA complète"
git push origin main --tags

# 2. Déploiement automatique (GitHub Actions)
# Voir .github/workflows/deploy.yml
```

### **Hotfixes urgents**
```bash
# Correction urgente en production
git checkout main
git checkout -b hotfix/cv-analysis-timeout
# ... correction ...
git commit -m "fix: timeout analyse CV pour gros fichiers"

# Merge vers main ET develop
git checkout main
git merge hotfix/cv-analysis-timeout
git checkout develop  
git merge hotfix/cv-analysis-timeout
```

## 📊 Monitoring équipe

### **Dashboard GitHub**
- **Issues**: Suivi bugs et features
- **Projects**: Kanban équipe
- **Actions**: CI/CD automatique
- **Insights**: Statistiques contribution

### **Métriques importantes**
- 🏃‍♂️ **Time to setup**: < 5 minutes
- ✅ **Test success rate**: > 95%
- 🚀 **Deploy frequency**: Quotidien
- 🐛 **Bug fix time**: < 24h

## 🆘 Support et dépannage

### **Problèmes fréquents**

#### ❌ "Conflit de merge"
```bash
# Résolution standard
git checkout develop
git pull origin develop
git checkout feature/ma-branche
git rebase develop
# Résoudre conflits manuellement
git rebase --continue
```

#### ❌ "Tests échouent après pull"
```bash
# Réinstallation propre
python install_project.py --clean
python test_installation_equipe.py
```

#### ❌ "Modèles IA non chargés"
```bash
# Forcer le téléchargement
cd CVAnalyserProject
python -c "from CVAnalyser.ai_services.cv_analyzer import CVAnalyzer; CVAnalyzer()"
```

### **Contacts support**
- **🤖 IA/ML**: @lead-ia (vous) - Modèles, analyse, performance
- **⚙️ Backend**: @dev-backend - API, Django, base de données  
- **🎨 Frontend**: @dev-frontend - Interface, UX, templates
- **🔧 DevOps**: @dev-devops - CI/CD, déploiement, infrastructure

## 📅 Planning équipe

### **Sprint actuel (Semaine 1)**
- [ ] **Tous**: Installation et test local
- [ ] **IA**: Optimisation temps chargement modèles
- [ ] **Backend**: API batch analysis
- [ ] **Frontend**: Dashboard résultats
- [ ] **QA**: Tests avec vrais CV entreprise

### **Sprint suivant (Semaine 2)**  
- [ ] **IA**: Modèle personnalisé métier
- [ ] **Backend**: Cache et performance
- [ ] **Frontend**: Interface admin
- [ ] **QA**: Tests de charge

### **Objectif mois**
🎯 **Déploiement production avec 1000+ CV analysés/jour**

---

## ✅ Checklist onboarding équipe

### **Développeur nouveau**
- [ ] Accès GitHub repository
- [ ] Clone et installation (`python install_project.py`)
- [ ] Tests réussis (`python test_installation_equipe.py`)
- [ ] Première branche feature créée
- [ ] Premier commit/PR soumis
- [ ] Review code par un senior
- [ ] Ajout au channel Slack/Teams équipe

### **Validation technique**
- [ ] Environnement local opérationnel
- [ ] IA chargée et fonctionnelle
- [ ] Serveur Django accessible
- [ ] Tests unitaires passent
- [ ] Workflow Git compris
- [ ] Conventions code respectées

**🎉 Bienvenue dans l'équipe Analyse CV IA !**
