import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
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
            raise ValidationError("Дата оконачния конкурса должна быть больше даты начала голосования")
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


class VideoParticipateForm(forms.ModelForm):
    comment = forms.CharField(label='Описание', widget=CKEditorWidget())
    content = forms.CharField(label='Ссылка на видео с youtube')

    class Meta:
        model = Participate
        fields = ('title', 'comment', 'content')

    def clean(self):
        form_data = self.cleaned_data
        video_link = form_data['content']
        if video_link:
            reg_exp = '^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|\?v=)([^#\&\?]*).*'
            match = re.match(reg_exp, video_link)
            if match and len(match.group(2)) == 11:
                form_data['content'] = 'https://www.youtube.com/embed/%s' % match.group(2)
                return form_data
            else:
                link = video_link.split('=')
                if len(link) > 1 and len(link[1]) == 11:
                    form_data['content'] = 'https://www.youtube.com/embed/%s' % link
                    return form_data
        self._errors["content"] = "Не корректная ссылка"
        del form_data['content']
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

