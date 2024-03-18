# models.py
from django.db import models

class Scholarship(models.Model):
    name = models.CharField(max_length=255,blank=True, null=True)
    amount = models.TextField(blank=True, null=True)
    deadline = models.CharField(max_length=255)
    eligibility_criteria= models.TextField(blank=True, null=True)
    image=models.ImageField(upload_to='scholarship_images/',null=True)
    apply = models.CharField(max_length=255,null=True)
    id= models.IntegerField(primary_key=True,null=False)

