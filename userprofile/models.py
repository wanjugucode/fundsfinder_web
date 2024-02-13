# profiles/models.py
from django.contrib.auth.models import User
from django.db import models
from jsonfield import JSONField

class UserProfile(models.Model):
    id= models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    contact_email = models.EmailField(null=True)
    telephone_number = models.CharField(max_length=20,null=True)
    optional_contact_phone = models.CharField(max_length=20,null=True)
    current_school = models.CharField(max_length=255,null=True)
    field_of_study = models.CharField(max_length=255,null=True)
    current_grade_level = models.CharField(max_length=10,null=True)
    cumulative_gpa = models.DecimalField(max_digits=4, decimal_places=2,null=True)
    personal_statement = models.TextField(null=True)
    optional_essay = models.TextField(null=True)
    reference_name = models.CharField(max_length=255,null=True)
    reference_email = models.EmailField(null=True)
    custom_fields = JSONField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
