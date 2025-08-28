from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription des utilisateurs"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role', 'first_name', 'last_name', 'phone')
        extra_kwargs = {
            'role': {'default': 'candidat'},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Identifiants invalides")
            if not user.is_active:
                raise serializers.ValidationError("Compte désactivé")
            data['user'] = user
        else:
            raise serializers.ValidationError("Username et password requis")
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'groups', 'created_at')
        read_only_fields = ('id', 'username', 'created_at', 'groups')


class UserListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des utilisateurs (admin/recruteur)"""
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'groups', 'created_at')
        read_only_fields = ('id', 'username', 'created_at', 'groups')
