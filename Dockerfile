# Dockerfile pour l'application Django CV Analyzer
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=CVAnalyzerProject.settings

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY CVAnalyzerProject/ ./CVAnalyzerProject/

# Création des répertoires nécessaires
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Collecte des fichiers statiques
WORKDIR /app/CVAnalyzerProject
RUN python manage.py collectstatic --noinput

# Création d'un utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Port d'exposition
EXPOSE 8000

# Script d'entrée
COPY docker-entrypoint.sh /docker-entrypoint.sh
USER root
RUN chmod +x /docker-entrypoint.sh
USER appuser

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "CVAnalyzerProject.wsgi:application"]
