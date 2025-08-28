# 🚀 GUIDE D'INSTALLATION POUR L'ÉQUIPE

## 📋 Prérequis
- **Python 3.8+** installé
- **Git** installé
- **Connexion internet** (pour télécharger les modèles IA - 1.4GB)
- **8GB RAM minimum** recommandé

## ⚡ Installation ultra-rapide

### **Étape 1: Récupérer le code**
```bash
git clone <votre-repo-github>
cd Analyse-CV-AI
```

### **Étape 2: Installation automatique**
```bash
python install_project.py
```
> ✅ Ce script fait TOUT automatiquement: environnement virtuel, dépendances, configuration Django

### **Étape 3: Lancer le serveur**

**Windows:**
```bash
# Option 1: Double-clic sur le fichier
start_server.bat

# Option 2: Ligne de commande
.venv\Scripts\python.exe CVAnalyserProject\manage.py runserver
```

**Linux/Mac:**
```bash
# Option 1: Script
./start_server.sh

# Option 2: Ligne de commande
.venv/bin/python CVAnalyserProject/manage.py runserver
```

### **Étape 4: Tester**
- Ouvrir: http://127.0.0.1:8000/
- Cliquer "Tester l'IA" → doit afficher "✅ IA opérationnelle!"

## ⏱️ Temps d'installation

- **Installation des packages**: 2-3 minutes
- **Premier lancement**: 1-2 minutes (téléchargement modèles IA)
- **Lancements suivants**: 30 secondes

## 🔧 Dépannage équipe

### ❌ "Python non trouvé"
```bash
# Vérifier l'installation Python
python --version
# Doit afficher Python 3.8+ 
```

### ❌ "Erreur installation packages"
```bash
# Mettre à jour pip
python -m pip install --upgrade pip
# Réessayer
python install_project.py
```

### ❌ "Modèles IA non chargés"
- **Attendre 1-2 minutes** au premier lancement
- Vérifier connexion internet
- Les modèles (1.4GB) se téléchargent automatiquement

### ❌ "Port 8000 déjà utilisé"
```bash
# Utiliser un autre port
python manage.py runserver 127.0.0.1:8001
```

## 🧪 Tests rapides

### Test 1: Vérifier l'installation
```bash
cd CVAnalyserProject
python test_ai_integration.py
```

### Test 2: API avec curl
```bash
curl http://127.0.0.1:8000/api/ai-status/
# Doit retourner: {"success": true, ...}
```

### Test 3: Interface web
- Aller sur http://127.0.0.1:8000/
- Uploader un CV test
- Voir l'analyse automatique

## 📱 Utilisation équipe

### **Pour les développeurs:**
- API REST: `http://127.0.0.1:8000/api/`
- Documentation: `README.md`
- Code IA: `CVAnalyser/ai_services/`

### **Pour les testeurs:**
- Interface web: `http://127.0.0.1:8000/`
- Uploader des CV réels
- Tester différents formats (PDF, DOCX, TXT)

### **Pour les responsables produit:**
- Voir les scores de correspondance
- Tester avec différents postes
- Évaluer la précision de l'IA

## 🆘 Support

### **En cas de problème:**
1. **Vérifier les prérequis** (Python 3.8+, internet)
2. **Relancer l'installation**: `python install_project.py`
3. **Redémarrer le serveur**: Ctrl+C puis relancer
4. **Vérifier les logs** dans le terminal
5. **Contacter l'équipe technique**

### **Contacts support:**
- **Lead IA**: [Votre nom] - Questions modèles et analyse
- **Backend**: [Nom] - Questions Django et API  
- **DevOps**: [Nom] - Questions installation et déploiement

## 📈 Performance attendue

### **Analyse d'un CV:**
- Upload: < 1 seconde
- Extraction texte: 1-2 secondes  
- Analyse IA: 2-5 secondes
- **Total: 5-10 secondes**

### **Correspondance CV/Poste:**
- Calcul similarité: 1-3 secondes
- **Résultat instantané**

## 🎯 Objectifs équipe

### **Sprint actuel:**
- [ ] Tous les membres testent l'installation
- [ ] Validation de l'interface web
- [ ] Tests avec vrais CV de l'entreprise
- [ ] Feedback sur la précision IA

### **Sprint suivant:**
- [ ] Intégration dans l'app principale
- [ ] Personnalisation des compétences métier
- [ ] Tests de charge
- [ ] Préparation déploiement production

---

## ✅ Checklist installation équipe

- [ ] Python 3.8+ installé
- [ ] Code récupéré depuis GitHub
- [ ] `python install_project.py` exécuté avec succès
- [ ] Serveur Django lancé
- [ ] Interface web accessible (http://127.0.0.1:8000/)
- [ ] Test IA réussi ("✅ IA opérationnelle!")
- [ ] Upload d'un CV test fonctionnel
- [ ] Score de correspondance calculé

**🎉 Installation réussie - Prêt à analyser des CV avec l'IA !**
