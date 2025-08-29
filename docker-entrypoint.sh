#!/bin/bash

# Script d'entrée Docker pour l'application CV Analyzer

set -e

echo "🚀 Démarrage de l'application CV Analyzer..."

# Attendre que PostgreSQL soit prêt
if [ "$DATABASE_URL" ]; then
    echo "⏳ Attente de la base de données..."
    python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db():
    db_url = "$DATABASE_URL"
    if not db_url:
        return
    
    parsed = urlparse(db_url)
    db_settings = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path[1:],
    }
    
    for attempt in range(30):
        try:
            conn = psycopg2.connect(**db_settings)
            conn.close()
            print("✅ Base de données prête!")
            return
        except psycopg2.OperationalError:
            print(f"⏳ Tentative {attempt + 1}/30 - Base de données non prête, attente...")
            time.sleep(2)
    
    print("❌ Impossible de se connecter à la base de données")
    sys.exit(1)

wait_for_db()
END
fi

# Migration de la base de données
echo "🔄 Application des migrations..."
python manage.py migrate --noinput

# Création d'un superutilisateur si les variables sont définies
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Création du superutilisateur..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        username='admin',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print("✅ Superutilisateur créé!")
else:
    print("ℹ️ Superutilisateur existe déjà")
END
fi

# Initialisation des groupes et données de test si en mode développement
if [ "$DJANGO_DEBUG" = "True" ]; then
    echo "🛠️ Initialisation des données de développement..."
    python manage.py init_groups || true
    python manage.py create_test_users || true
fi

# Téléchargement des modèles NLTK si nécessaire
echo "📚 Vérification des données NLTK..."
python << END
import nltk
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    print("✅ Données NLTK disponibles")
except LookupError:
    print("📥 Téléchargement des données NLTK...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    print("✅ Données NLTK téléchargées")
END

echo "🎉 Application prête! Démarrage du serveur..."

# Exécution de la commande passée en argument
exec "$@"
