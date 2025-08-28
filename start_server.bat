@echo off
echo 🚀 Lancement du serveur Django avec IA...
echo.
echo Chargement des modèles IA (1-2 minutes au premier lancement)...
echo.
cd CVAnalyserProject
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
echo.
echo 🌐 Interface web: http://127.0.0.1:8000/
echo.
pause
