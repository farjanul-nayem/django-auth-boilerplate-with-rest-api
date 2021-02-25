from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import pre_save
from .utils import rand_uid  


class UserProfileManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone=None, bio=None, website=None, avatar=None, password=None):

        if not email:
            raise ValueError('User must have an email address')
        if not first_name:
            raise ValueError('User must have an first name')
        if not last_name:
            raise ValueError('User must have an last name')
        if not password:
            raise ValueError('User must have an password')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            bio=bio,
            website=website,
            avatar=avatar
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, first_name, last_name, phone=None, bio=None, website=None, avatar=None, password=None):
        user = self.create_user(
            email,
            first_name,
            last_name,
            phone=phone,
            bio=bio,
            website=website,
            avatar=avatar,
            password=password
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone=None, bio=None, website=None, avatar=None, password=None):

        user = self.create_user(
            email,
            first_name,
            last_name,
            phone=phone,
            bio=bio,
            website=website,
            avatar=avatar,
            password=password
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    uid = models.CharField(max_length=8, unique=True)
    is_active = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserProfileManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_first_name(self):
        return f'{self.first_name}'

    def get_last_name(self):
        return f'{self.last_name}'

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    # @property
    # def is_active(self):
    #     return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin


def get_uid(instance, uid=None):
    _uid = rand_uid()
    if uid is not None:
        _uid = uid

    qs = UserProfile.objects.filter(uid=_uid)
    exists = qs.exists()
    if exists:
        _uid = rand_uid()
    return _uid


def user_pre_save(signal, instance, sender, **kwargs):
    if not instance.uid:
        instance.uid = get_uid(instance)


pre_save.connect(user_pre_save, sender=UserProfile)
