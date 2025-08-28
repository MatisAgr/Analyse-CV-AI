#!/bin/bash
echo "🚀 Lancement du serveur Django avec IA..."
echo ""
echo "Chargement des modèles IA (1-2 minutes au premier lancement)..."
echo ""
cd CVAnalyserProject
../.venv/bin/python manage.py runserver 127.0.0.1:8000
