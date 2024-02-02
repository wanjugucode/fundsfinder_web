from django import forms
from.models import *

class ScholashipAdditionForm(forms.ModelForm):
    class Meta:
        model=Scholarships
        fields=['name','description','eligibility_criteria','scholarship_type','application_deadline','Contact_email']
class ScholarshipApplicationForm(forms.ModelForm):
    class Meta:
        model = ScholarshipApplication
        fields = ['name', 'email', 'essay'] 