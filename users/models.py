"""
users/models.py
───────────────
Extends Django's AbstractUser to add:
  • role  — 'citizen' or 'admin'
  • phone — optional contact number
  • avatar — profile picture
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('admin',   'Admin'),
    ]

    role   = models.CharField(max_length=10, choices=ROLE_CHOICES, default='citizen')
    phone  = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_civic_admin(self):
        return self.role == 'admin' or self.is_staff
