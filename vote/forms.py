from django import forms

from .models import Competition


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ('title', 'Type')

