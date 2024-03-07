from django import forms
from.models import *

class ScholarshipAdditionForm(forms.ModelForm):
    class Meta:
        model=Scholarships
        fields=['name','description','eligibility_criteria','scholarship_type','application_deadline','Contact_email']





class ScholarshipApplicationForm(forms.ModelForm):
    class Meta:
        model = ScholarshipApplication
        fields = [ 'essay'] 
class CommentForm(forms.ModelForm):
    class Meta:
        model = ScholarshipComment
        fields = ['comment']
class RatingForm(forms.Form):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
class ReportForm(forms.ModelForm):
    class Meta:
        model = ReportInaccuracy
        fields = ['description']