from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser



class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    # Add more profile-related fields as needed

    def __str__(self):
        return self.user.username
    
class UserLoginActivity(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    login_timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    # Add more fields to track user activity

    def __str__(self):
        return f"{self.user.username} - {self.login_timestamp}"
