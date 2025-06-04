from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

def validate_age(date_naissance):
    """Validation personnalisée pour vérifier l'âge minimum"""
    today = date.today()
    
    # Vérifier que la date n'est pas dans le futur
    if date_naissance > today:
        raise ValidationError(
            "La date de naissance ne peut pas être dans le futur."
        )
    
    # Calculer l'âge
    age = today.year - date_naissance.year
    
    # Ajuster si l'anniversaire n'est pas encore passé cette année
    if today.month < date_naissance.month or \
       (today.month == date_naissance.month and today.day < date_naissance.day):
        age -= 1
    
    # Vérifier l'âge minimum
    if age < 12:
        raise ValidationError(
            f"Vous devez avoir au moins 12 ans pour créer un compte. "
            f"Vous avez actuellement {age} ans."
        )

class UseManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Créer et retourner un nouvel utilisateur"""
        if not email:
            raise ValueError("L'utilisateur doit saisir son email")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Créer et retourner un superutilisateur"""
        # Les superusers n'ont pas besoin des champs personnalisés
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser doit avoir is_superuser=True.')
        
        user = self.create_user(email, password, **extra_fields)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    choix_genre = [
        ('H', 'Homme'),
        ('F', 'Femme')
    ]
    genre = models.CharField(
        max_length=1, 
        choices=choix_genre, 
        blank=True,
        null=True  # Permet NULL pour les superusers
    )
    date_naissance = models.DateField(
        blank=True, 
        null=True,  # Permet NULL pour les superusers
        validators=[validate_age]  # Ajouter la validation d'âge
    )

    objects = UseManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def get_age(self):
        """Calculer et retourner l'âge de l'utilisateur"""
        if not self.date_naissance:
            return None
        
        today = date.today()
        age = today.year - self.date_naissance.year
        
        if today.month < self.date_naissance.month or \
           (today.month == self.date_naissance.month and today.day < self.date_naissance.day):
            age -= 1
        
        return age

    def clean(self):
        """Validation au niveau du modèle"""
        super().clean()
        
        # Pour les utilisateurs normaux, ces champs sont requis
        if not self.is_superuser:
            if not self.date_naissance:
                raise ValidationError({
                    'date_naissance': 'La date de naissance est requise.'
                })
            if not self.genre:
                raise ValidationError({
                    'genre': 'Le genre est requis.'
                })