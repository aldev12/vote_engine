from django import forms

from .models import Competition, Participate


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ('title', 'Type', 'Rules', 'Description', 'expiry_date', 'Survey_date')


class ParticipateForm(forms.ModelForm):
    class Meta:
        model = Participate
        fields = ('title', 'Comment', 'Content')

