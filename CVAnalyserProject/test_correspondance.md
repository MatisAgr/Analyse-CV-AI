## Test de Correspondance CV-Poste

### Problème résolu :
❌ **Erreur précédente :** "Unexpected token '<'"
✅ **Cause :** Décorateur `@csrf_exempt` manquant sur la vue `analyze_cv_for_job`
✅ **Solution :** Ajout du décorateur + amélioration de la gestion d'erreurs JS

### Test de fonctionnement :

1. **Aller sur** http://127.0.0.1:8000/
2. **Uploader un CV** (PDF/DOCX/TXT)
3. **Attendre l'analyse** (∼30s)
4. **Saisir description de poste** dans le champ texte
5. **Cliquer "Calculer correspondance"**

### Résultats attendus :
```
✅ Scores de correspondance
Score global: XX%
Similarité sémantique: XX%
Correspondance compétences: XX%
```

### Si erreur :
- Message détaillé avec type d'erreur
- Plus d'information "Unexpected token '<'"

### APIs disponibles :
- `POST /api/analyze-cv-job/` - Correspondance CV-poste
- `POST /api/upload-cv/` - Upload et analyse CV
- `GET /api/ai-status/` - Statut des modèles IA
