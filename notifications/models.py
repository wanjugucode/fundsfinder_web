from django.db import models

# Create your models here.
class Notification(models.Model):
    userprofile = models.ForeignKey('userprofile.UserProfile', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    id= models.IntegerField(primary_key=True)




