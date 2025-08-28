# Étape 3 : Tests des Endpoints API (avec EMAIL)

## Endpoints disponibles

### 1. Inscription (POST /api/register/)
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username":"Test"
    "password": "motdepasse123",
    "password_confirm": "motdepasse123",
    "role": "candidat",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Connexion (POST /api/login/)
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "motdepasse123"
  }'
```

### 3. Profil utilisateur (GET /api/users/me/)
```bash
# Avec Basic Auth (email:password)
curl -u test@example.com:motdepasse123 http://127.0.0.1:8000/api/users/me/

# Avec JWT Token (récupéré du login)
curl -H "Authorization: Bearer TON_ACCESS_TOKEN" http://127.0.0.1:8000/api/users/me/
```

### 4. Liste des utilisateurs (GET /api/users/) - Admin/Recruteur seulement
```bash
curl -u admin@test.com:password http://127.0.0.1:8000/api/users/
curl -u admin@test.com:password "http://127.0.0.1:8000/api/users/?role=candidat"
```

### 5. Modifier profil (PUT /api/users/me/update/)
```bash
curl -X PUT http://127.0.0.1:8000/api/users/me/update/ \
  -u test@example.com:motdepasse123 \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Nouveau Prénom",
    "phone": "0123456789"
  }'
```

## Tests de permissions à faire

1. **Candidat** peut :
   - ✅ S'inscrire
   - ✅ Se connecter  
   - ✅ Voir son profil
   - ✅ Modifier son profil
   - ❌ Voir la liste des utilisateurs
   - ❌ Accéder à admin-only

2. **Recruteur** peut :
   - ✅ Tout ce que peut faire un candidat
   - ✅ Voir la liste des utilisateurs
   - ❌ Accéder à admin-only

3. **Admin** peut :
   - ✅ Tout faire

## Avec Postman
Importe ces endpoints dans Postman et teste avec différents utilisateurs !
