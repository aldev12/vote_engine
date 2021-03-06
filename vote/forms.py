import re

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Competition, Participate, Profile
from .validators import validate_photo_file_extension, validate_audio_file_extension


class CompetitionForm(forms.ModelForm):
    rules = forms.CharField(label='Правила', widget=CKEditorWidget())
    short_description = forms.CharField(label='Краткое описание', widget=CKEditorWidget())
    expiry_date = forms.DateField(label="Дата окончания",
                                  required=True,
                                  initial=timezone.now() + timezone.timedelta(days=30))
    survey_date = forms.DateField(label="Голосование с",
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
            raise ValidationError("Дата оконачния конкурса должна быть больше даты начала голосования")
        return cd


class PhotoParticipateForm(forms.ModelForm):
    comment = forms.CharField(label='Описание', widget=CKEditorWidget())
    content_file = forms.FileField(label='Файл',
                                   validators=[validate_photo_file_extension],
                                   help_text='Возможные расширения: ".jpg", ".jpeg"')

    class Meta:
        model = Participate
        fields = ('title', 'comment', 'content_file')


class AudioParticipateForm(forms.ModelForm):
    comment = forms.CharField(label='Описание', widget=CKEditorWidget())
    content_file = forms.FileField(label='Файл',
                                   validators=[validate_audio_file_extension],
                                   help_text='Возможные расширения:".mp3", ".ogg", ".wav"')

    class Meta:
        model = Participate
        fields = ('title', 'comment', 'content_file')


class LiteralParticipateForm(forms.ModelForm):
    comment = forms.CharField(label='Текст', widget=CKEditorWidget())

    class Meta:
        model = Participate
        fields = ('title', 'comment')


class VideoParticipateForm(forms.ModelForm):
    comment = forms.CharField(label='Описание', widget=CKEditorWidget())
    content_file = forms.CharField(label='Ссылка на видео с youtube')

    class Meta:
        model = Participate
        fields = ('title', 'comment', 'content_file')

    def clean(self):
        super(VideoParticipateForm, self).clean()
        form_data = self.cleaned_data
        video_link = form_data['content_file']
        if video_link:
            reg_exp = '^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|\?v=)([^#\&\?]*).*'
            match = re.match(reg_exp, video_link)
            if match and len(match.group(2)) == 11:
                form_data['content_file'] = 'https://www.youtube.com/embed/%s' % match.group(2)
            else:
                link = video_link.split('=')
                if len(link) > 1 and len(link[1]) == 11:
                    form_data['content_file'] = 'https://www.youtube.com/embed/%s' % link
        if video_link == form_data['content_file']:
            self._errors["content_file"] = ["Некорректная ссылка"]
            del form_data['content_file']
        return form_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'location', 'birth_date')


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Обязательное поле')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

