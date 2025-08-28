from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription des utilisateurs"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'role', 'first_name', 'last_name', 'phone')
        extra_kwargs = {
            'role': {'default': 'candidat'},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Générer un username à partir de l'email
        email = validated_data['email']
        username = email.split('@')[0]
        
        # Vérifier l'unicité du username et ajouter un numéro si nécessaire
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Ajouter le username aux données validées
        validated_data['username'] = username
        
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Chercher l'utilisateur par email d'abord
            try:
                user_obj = User.objects.get(email=email)
                print(f"DEBUG: User trouvé: {user_obj.username}, {user_obj.email}")
                
                # Puis authentifier avec le username trouvé
                user = authenticate(username=user_obj.username, password=password)
                print(f"DEBUG: Authentification résultat: {user}")
                
                if not user:
                    # Essayer aussi avec l'email directement
                    user = authenticate(username=email, password=password)
                    print(f"DEBUG: Authentification avec email: {user}")
                    
            except User.DoesNotExist:
                print(f"DEBUG: Aucun utilisateur trouvé avec email: {email}")
                user = None
                
            if not user:
                raise serializers.ValidationError("Identifiants invalides")
            if not user.is_active:
                raise serializers.ValidationError("Compte désactivé")
            data['user'] = user
        else:
            raise serializers.ValidationError("Email et password requis")
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'role', 'groups', 'created_at')
        read_only_fields = ('id', 'email', 'created_at', 'groups')


class UserListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des utilisateurs (admin/recruteur)"""
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'groups', 'created_at')
        read_only_fields = ('id', 'created_at', 'groups')
