from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django_currentuser.middleware import get_current_authenticated_user

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
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('state', 'pending')
        return self._create_user(user_email, user_username, password, **extra_fields)

    def create_superuser(self, user_email, user_username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('state', 'approved')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(user_email, user_username, password, **extra_fields)

class Structure(models.Model):
    structure_id = models.AutoField(primary_key=True)
    structure_varchar = models.CharField(max_length=255)
    structure_code = models.CharField(max_length=50)
    structure_cree_par = models.CharField(max_length=50, blank=True, null=True)
    structure_cree_date = models.DateTimeField(default=timezone.now)
    structure_miseajour_par = models.CharField(max_length=50, blank=True, null=True)
    structure_miseajour_date = models.DateTimeField(auto_now=True)
    structure_niveau = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        if user:
            if not self.pk:  # New instance
                self.structure_cree_par = user.user_username
            self.structure_miseajour_par = user.user_username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.structure_varchar

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=255)
    department_code = models.CharField(max_length=50, unique=True)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='departments')
    department_cree_par = models.CharField(max_length=50, blank=True, null=True)
    department_cree_date = models.DateTimeField(default=timezone.now)
    department_miseajour_par = models.CharField(max_length=50, blank=True, null=True)
    department_miseajour_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        if user:
            if not self.pk:  # New instance
                self.department_cree_par = user.user_username
            self.department_miseajour_par = user.user_username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.department_name} ({self.structure.structure_varchar})"

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    user_firstname = models.CharField(max_length=50)
    user_lastname = models.CharField(max_length=50)
    user_username = models.CharField(max_length=50, unique=True)
    user_email = models.EmailField(unique=True)
    user_password = models.CharField(max_length=128)
    user_cree_par = models.CharField(max_length=50, blank=True, null=True)
    user_cree_date = models.DateTimeField(default=timezone.now)
    user_miseajour_par = models.CharField(max_length=50, blank=True, null=True)
    user_miseajour_date = models.DateTimeField(auto_now=True, null=True)
    user_role = models.CharField(max_length=50, choices=[
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('department_chief', 'Department Chief'),
        ('DRH', 'DRH'),
        ('admin', 'Admin'),
    ])
    structure = models.ForeignKey(Structure, on_delete=models.SET_NULL, related_name='users', null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    state = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_username', 'user_firstname', 'user_lastname', 'user_role']

    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        if user:
            if not self.pk:  # New instance
                self.user_cree_par = user.user_username
            self.user_miseajour_par = user.user_username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user_username

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
    formation_category = models.CharField(max_length=50, choices=[
        ('geophysique', 'Géophysique'),
        ('forage_petrole', 'Forage Pétrolier'),
        ('production_des_hydrocarbures', 'Production des Hydrocarbures'),
        ('transport_des_hydrocarbures', 'Transport des Hydrocarbures'),
        ('exploitation_des_hydrocarbures', 'Exploitation des Hydrocarbures'),
        ('genie_du_gaz', 'Génie du Gaz'),
        ('raffinage', 'Raffinage'),
        ('chimie_et_analyse_des_hydrocarbures', 'Chimie et Analyse des Hydrocarbures'),
        ('instrumentation_petroliere', 'Instrumentation Pétrolière'),
        ('maintenance_industrielle', 'Maintenance Industrielle'),
        ('securite_industrielle_et_environnement', 'Sécurité Industrielle et Environnement'),
        ('economie_petroliere', 'Économie Pétrolière'),
        ('energies_nouvelles_et_renouvelables', 'Énergies Nouvelles et Renouvelables'),
    ])
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formations', null=True)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='formations')

    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        if user:
            if not self.pk:  # New instance
                self.formation_mise_a_jour_cree = user.user_username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.formation_titre

class UserFormation(models.Model):
    user_formation_id = models.AutoField(primary_key=True)
    date_inscription = models.DateTimeField(default=timezone.now)
    state_formation = models.CharField(max_length=50)
    valide_par = models.CharField(max_length=50, blank=True, null=True)
    valide_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_formations')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='user_formations')

    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        if user:
            if not self.pk:  # New instance
                self.valide_par = user.user_username
        super().save(*args, **kwargs)

    def valider_par(self, validator):
        self.valide_par = validator
        self.valide_date = timezone.now()
        self.state_formation = 'validated'
        self.save()
        Notification.objects.create(
            user=self.user,
            message=f"Your participation in '{self.formation.formation_titre}' has been validated."
        )

    def annuler_inscription(self):
        self.state_formation = 'cancelled'
        self.save()
        Notification.objects.create(
            user=self.user,
            message=f"Your participation in '{self.formation.formation_titre}' has been cancelled."
        )

    def __str__(self):
        return f"{self.user.user_username} - {self.formation.formation_titre}"

class Notification(models.Model):
    objects = None
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        if user:
            if not self.pk:  # New instance
                self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification for {self.user.user_username}: {self.message[:50]}"

    class Meta:
        ordering = ['-created_at']