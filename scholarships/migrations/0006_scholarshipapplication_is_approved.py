# Generated by Django 5.0.1 on 2024-01-30 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0005_scholarshipapplication_scholarships_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='scholarshipapplication',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
