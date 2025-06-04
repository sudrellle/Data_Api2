from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les objets utilisateur"""
    
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'genre', 'date_naissance']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def validate_date_naissance(self, value):
        """Validation personnalisée pour la date de naissance"""
        if not value:
            raise serializers.ValidationError("La date de naissance est requise.")
        
        today = date.today()
        
        # Vérifier que la date n'est pas dans le futur
        if value > today:
            raise serializers.ValidationError(
                "La date de naissance ne peut pas être dans le futur."
            )
        
        # Calculer l'âge
        age = today.year - value.year
        
        # Ajuster si l'anniversaire n'est pas encore passé cette année
        if today.month < value.month or \
           (today.month == value.month and today.day < value.day):
            age -= 1
        
        # Vérifier l'âge minimum
        if age < 12:
            raise serializers.ValidationError(
                f"Vous devez avoir au moins 12 ans pour créer un compte. "
                f"Vous avez actuellement {age} ans."
            )
        
        return value

    def validate_genre(self, value):
        """Validation pour le genre"""
        if not value:
            raise serializers.ValidationError("Le genre est requis.")
        return value

    def validate(self, data):
        """Validation globale"""
        # Vérifier que les champs requis sont présents pour les utilisateurs normaux
        if not data.get('date_naissance'):
            raise serializers.ValidationError({
                'date_naissance': 'La date de naissance est requise.'
            })
        
        if not data.get('genre'):
            raise serializers.ValidationError({
                'genre': 'Le genre est requis.'
            })
        
        return data

    def create(self, validated_data):
        """Créer et retourner un nouvel utilisateur avec mot de passe crypté"""
        try:
            return get_user_model().objects.create_user(**validated_data)
        except DjangoValidationError as e:
            # Convertir les erreurs Django en erreurs DRF
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        """Mettre à jour et retourner un utilisateur"""
        print("update called with:", validated_data)
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        print("Updated user:", user.name)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer pour l'authentification par token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Valider et authentifier l'utilisateur"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        
        # Vérifier que l'utilisateur est actif
        if not user.is_active:
            msg = _('User account is disabled')
            raise serializers.ValidationError(msg, code='authorization')
            
        attrs['user'] = user
        return attrs