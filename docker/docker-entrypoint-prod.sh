#!/bin/bash

set -e

echo "🚀 Démarrage du CV Analyzer en mode PRODUCTION"

# Fonction d'attente pour PostgreSQL
wait_for_postgres() {
    echo "⏳ Attente de PostgreSQL..."
    
    while ! pg_isready -h db -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB; do
        echo "PostgreSQL n'est pas encore prêt - attente de 2 secondes..."
        sleep 2
    done
    
    echo "✅ PostgreSQL est prêt!"
}

# Fonction d'attente pour Redis
wait_for_redis() {
    echo "⏳ Attente de Redis..."
    
    while ! redis-cli -h redis -p 6379 -a $REDIS_PASSWORD ping; do
        echo "Redis n'est pas encore prêt - attente de 2 secondes..."
        sleep 2
    done
    
    echo "✅ Redis est prêt!"
}

# Attendre les services
wait_for_postgres
wait_for_redis

# Migration de la base de données
echo "📊 Application des migrations..."
python manage.py migrate --noinput

# Collecte des fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# Création du superutilisateur
echo "👤 Création du superutilisateur..."
python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password
    )
    print(f"Superutilisateur créé: {email}")
else:
    print("Superutilisateur existe déjà ou variables manquantes")
EOF

# Téléchargement des données NLTK en arrière-plan
echo "📚 Téléchargement des données NLTK..."
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    print('✅ Données NLTK téléchargées')
except Exception as e:
    print(f'⚠️ Erreur NLTK: {e}')
" &

# Validation de la configuration
echo "🔍 Validation de la configuration Django..."
python manage.py check --deploy

echo "🎯 Configuration terminée - Démarrage de l'application..."

# Exécution de la commande passée en argument
exec "$@"
