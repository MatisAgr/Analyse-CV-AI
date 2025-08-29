from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Candidature


class UserRegistrationSerializer(serializers.ModelSerializer):
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
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'role', 'groups', 'created_at')
        read_only_fields = ('id', 'email', 'created_at', 'groups')


class UserListSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'groups', 'created_at')
        read_only_fields = ('id', 'created_at', 'groups')


class CandidatureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = ('poste', 'entreprise', 'cv', 'lettre_motivation')
        
    def validate_cv(self, value):
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError("Le CV ne peut pas dépasser 5MB")
        return value
    
    def validate_lettre_motivation(self, value):
        if value and value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError("La lettre ne peut pas dépasser 5MB")
        return value
    
    def create(self, validated_data):
        # ajouter automatiquement le candidat connecté
        validated_data['candidat'] = self.context['request'].user
        return super().create(validated_data)


class CandidatureListSerializer(serializers.ModelSerializer):
    """Serializer pour lister les candidatures"""
    candidat = UserProfileSerializer(read_only=True)
    cv_url = serializers.SerializerMethodField()
    lettre_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidature
        fields = (
            'id', 'candidat', 'poste', 'entreprise', 'status', 
            'cv_url', 'lettre_url', 'score_ia', 'competences_extraites',
            'created_at', 'updated_at', 'commentaires'
        )
    
    def get_cv_url(self, obj):
        if obj.cv:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cv.url)
        return None
    
    def get_lettre_url(self, obj):
        if obj.lettre_motivation:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.lettre_motivation.url)
        return None


class CandidatureUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour modifier une candidature (recruteurs)"""
    
    class Meta:
        model = Candidature
        fields = ('status', 'commentaires', 'score_ia')
    
    def validate_status(self, value):
        """Validation du statut"""
        user = self.context['request'].user
        
        # Seuls les recruteurs et admins peuvent changer le statut
        if user.role not in ['admin', 'recruteur']:
            raise serializers.ValidationError("Seuls les recruteurs peuvent modifier le statut")
        
        return value
