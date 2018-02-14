from django import forms

from .models import Competition, Participate


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ('title', 'comp_type', 'rules', 'short_description', 'expiry_date', 'survey_date')


class ParticipateForm(forms.ModelForm):
    class Meta:
        model = Participate
        fields = ('title', 'comment', 'content')


class UserRegistrationForm(forms.Form):
    username = forms.CharField(
        required=True,
        label='Имя пользователя',
        max_length=32
    )
    email = forms.CharField(
        required=True,
        label='Email',
        max_length=32,
    )
    password = forms.CharField(
        required=True,
        label='Пароль',
        max_length=32,
        widget=forms.PasswordInput()
    )
