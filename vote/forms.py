from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Competition, Participate, Profile
from ckeditor.widgets import CKEditorWidget
from django.forms.extras import SelectDateWidget


class CompetitionForm(forms.ModelForm, forms.Field):
    rules = forms.CharField(label='Правила', widget=CKEditorWidget())
    short_description = forms.CharField(label='Краткое описание', widget=CKEditorWidget())
    expiry_date = forms.DateField(label="Дата окончания", widget=SelectDateWidget(), required=True)
    survey_date = forms.DateField(label="Голосование с",
                                  widget=SelectDateWidget(),
                                  required=True,
                                  initial=timezone.now() + timezone.timedelta(days=5))

    class Meta:
        model = Competition
        fields = ('title', 'comp_type', 'rules', 'short_description', 'expiry_date', 'survey_date')

    def clean(self):
        cd = self.cleaned_data
        expiry_date = cd.get("expiry_date")
        survey_date = cd.get("survey_date")
        if expiry_date <= survey_date:
            raise ValidationError("Дата оконачния онкурса должна быть больше даты начала голосавания")
        return cd


class ParticipateForm(forms.ModelForm):
    comment = forms.CharField(label='Описание', widget=CKEditorWidget())

    class Meta:
        model = Participate
        fields = ('title', 'comment', 'content')


class LiteralParticipateForm(forms.ModelForm):
    comment = forms.CharField(label='Контент', widget=CKEditorWidget())

    class Meta:
        model = Participate
        fields = ('title', 'comment')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'location', 'birth_date')


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
