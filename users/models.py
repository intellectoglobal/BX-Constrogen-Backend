from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from client.models import Company, Clientbase


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user_name, filename)


class CustomAccountManager(BaseUserManager):
    # JUST TO SIMPLYFY THE USER MODLE OBJECTS PROPERTIES
    def create_superuser(self, email, user_name, first_name, last_name, password, **other_fields):
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        return self.create_user(email, user_name, first_name, last_name, password, ** other_fields)

    def create_clientuser(self, email, user_name, first_name, last_name, password, **other_fields):
        other_fields.setdefault('is_superuser', False)
        other_fields.setdefault('is_active', True)
        return self.create_user(email, user_name, first_name, last_name, password, ** other_fields)

    def create_user(self, email, user_name, first_name, last_name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,
                          first_name=first_name, last_name=last_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class AppRolePermissionManager(models.Manager):
    # JUST TO SIMPLYFY THE USER MODLE OBJECTS PROPERTIES
    def checkRolePermissionExists(self, role_id, permission_ids):
        for permission in permission_ids:
            return len(super().get_queryset().filter(role_id=role_id, permission_id=permission)) > 0

    def checkSingleRolePermissionExists(self, role_id, permission_ids):
        return len(super().get_queryset().filter(role_id=role_id, permission_id=permission_ids)) > 0

    def get_queryset(self):
        return super().get_queryset().all()


class AppPermission(models.Model):
    permission = models.CharField(max_length=150, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.permission


class AppRole(models.Model):
    role = models.CharField(max_length=250, unique=True)
    role_description = models.CharField(max_length=250)
    is_role_active = models.BooleanField(default=True)
    REQUIRED_FIELDS = ['role', 'role_description']

    def __str__(self):
        return self.role


class AppRolePermission(models.Model):
    role = models.ForeignKey(AppRole, on_delete=models.CASCADE)
    permission = models.ForeignKey(AppPermission, on_delete=models.CASCADE)
    description = models.CharField(max_length=250)
    objects = AppRolePermissionManager()

    def __str__(self):
        return str(self.role) + " -- " + str(self.permission)


class AppUser(AbstractBaseUser, PermissionsMixin, models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Invalid Phonenumber")
    user_name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_('email address'))
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)
    profile_pic = models.ImageField(
        upload_to=user_directory_path, max_length=254, blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    objects = CustomAccountManager()
    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.user_name


class AppUsersRole(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    role = models.ForeignKey(AppRole, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.user_name) + " - "+str(self.role.role)


class Authentication(models.Model):
    AUTH_STATUS_CHOICES = (
        ('pending', 'PENDING'),
        ('success', 'SUCCESS'),
        ('failed', 'FAILED'),
    )

    email = models.CharField(max_length=255, null=False, blank=False)
    session = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10, choices=AUTH_STATUS_CHOICES, default='pending')
    user = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, null=True, blank=True)
    login_date = models.DateTimeField(default=timezone.now)

    def get(self):
        return self.email


class UserSettings(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    option = models.CharField(max_length=200, null=True, blank=True)
    value = models.CharField(max_length=200, null=True, blank=True)


class AppUserCompany(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.user_name) + " - "+str(self.company.name)
