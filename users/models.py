from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def _create_user(self, user_email, user_username, password=None, **extra_fields):
        if not user_email:
            raise ValueError("The Email field must be set")
        if not user_username:
            raise ValueError("The Username field must be set")
        user_email = self.normalize_email(user_email)
        user = self.model(user_email=user_email, user_username=user_username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, user_email, user_username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(user_email, user_username, password, **extra_fields)

    def create_superuser(self, user_email, user_username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(user_email, user_username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    user_firstname = models.CharField(max_length=50)
    user_lastname = models.CharField(max_length=50)
    user_username = models.CharField(max_length=50, unique=True)
    user_email = models.EmailField(unique=True)
    user_password = models.CharField(max_length=128)  # Handled by set_password
    user_cree_par = models.CharField(max_length=50, blank=True, null=True)
    user_cree_date = models.DateTimeField(default=timezone.now)
    user_miseajour_par = models.CharField(max_length=50, blank=True, null=True)
    user_miseajour_date = models.DateTimeField(auto_now=True)
    user_role = models.CharField(max_length=50)

    # Required fields for AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_username', 'user_firstname', 'user_lastname', 'user_role']

    def __str__(self):
        return self.user_username

class Structure(models.Model):
    structure_id = models.AutoField(primary_key=True)
    structure_varchar = models.CharField(max_length=255)
    structure_code = models.CharField(max_length=50)
    structure_cree_par = models.CharField(max_length=50, blank=True, null=True)
    structure_cree_date = models.DateTimeField(default=timezone.now)
    structure_miseajour_par = models.CharField(max_length=50, blank=True, null=True)
    structure_miseajour_date = models.DateTimeField(auto_now=True)
    structure_niveau = models.CharField(max_length=50)

    # Many-to-many relationship with User
    users = models.ManyToManyField(User, related_name='structures')

    def __str__(self):
        return self.structure_varchar

class Formation(models.Model):
    formation_id = models.AutoField(primary_key=True)
    formation_titre = models.CharField(max_length=255)
    formation_ref = models.CharField(max_length=50)
    formation_niveau = models.CharField(max_length=50)
    formation_description = models.TextField()
    formation_cout = models.IntegerField()
    formation_mise_a_jour_cree = models.CharField(max_length=50, blank=True, null=True)
    formation_mise_a_jour_date = models.DateTimeField(auto_now=True)
    formation_pays = models.CharField(max_length=50)
    formation_duree = models.IntegerField()
    formation_prerequis = models.CharField(max_length=255, blank=True, null=True)
    formation_programme = models.TextField(blank=True, null=True)
    formation_cible = models.TextField(blank=True, null=True)
    formation_objectif = models.TextField(blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formations')

    def __str__(self):
        return self.formation_titre

class Session(models.Model):
    session_id = models.AutoField(primary_key=True)
    session_debut_date = models.DateTimeField()
    session_fin_date = models.DateTimeField()
    session_cree_par = models.CharField(max_length=50, blank=True, null=True)
    session_cree_date = models.DateTimeField(default=timezone.now)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='sessions')
    participants = models.ManyToManyField(User, related_name='sessions')

    def __str__(self):
        return f"Session for {self.formation.formation_titre}"

class UserFormation(models.Model):
    user_formation_id = models.AutoField(primary_key=True)
    date_inscription = models.DateTimeField(default=timezone.now)
    state_formation = models.CharField(max_length=50)
    valide_par = models.CharField(max_length=50, blank=True, null=True)
    valide_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_formations')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='user_formations')

    def __str__(self):
        return f"{self.user.user_username} - {self.formation.formation_titre}"