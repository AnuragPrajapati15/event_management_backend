from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, role="User"):
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(username=username, role=role)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password, role="Admin")
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    total_tickets = models.IntegerField()
    tickets_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.quantity})"
