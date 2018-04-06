from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from hitcount.models import HitCountMixin, HitCount
from mezzanine.core.fields import RichTextField
from mezzanine.pages.models import Page, RichText


class Profile(models.Model):
    """Расширили стандартную пользовательскую модель"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField('номер телефона', max_length=15, null=True, blank=True)
    location = models.CharField('город', max_length=30, blank=True)
    birth_date = models.DateField('дата рождения', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


# Сигналы на автообновление Profile после изменений в User (post_save)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Competition(Page, HitCountMixin):
    """Модель конкурса"""
    PHOTO = 1
    LITERAL = 2
    VIDEO = 3
    AUDIO = 4
    COMPETITION_TYPE = (
        (PHOTO, 'Фотоконкурс'),
        (LITERAL, 'Литературный конкурс'),
        (VIDEO, 'Видеоконкурс'),
        (AUDIO, 'Аудиоконкурс'),
    )

    survey_date = models.DateTimeField(
        'голосование с',
        default=timezone.now() + timezone.timedelta(days=5))
    comp_type = models.IntegerField(
        'тип конкурса',
        default=PHOTO,
        choices=COMPETITION_TYPE)
    rules = RichTextField('правила', max_length=2000)
    short_description = RichTextField('краткое описание', max_length=500)
    creator = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='competition_user',
        on_delete=models.CASCADE)
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')

    @property
    def type_str(self):
        return dict(Competition.COMPETITION_TYPE)[self.comp_type]

    @property
    def status_str(self):
        status = "Завершен"
        if self.expiry_date > timezone.now():
            if timezone.now() < self.survey_date:
                status = "Прием заявок"
            else:
                status = "Идет голосование"
        return status

    class Meta:
        verbose_name = 'конкурс'
        verbose_name_plural = 'конкурсы'


class Participate(Page):
    """Модель заявки на участие"""
    comment = RichTextField('описание')
    competition_id = models.ForeignKey(
        'Competition',
        verbose_name='конкурс',
        related_name='competition_participates',
        on_delete=models.CASCADE)
    content_file = models.FileField('файл',
                                    upload_to='uploads/%Y/%m/%d/',
                                    blank=True,
                                    null=True)
    creator = models.ForeignKey(
        User, verbose_name='автор',
        related_name='user_participates',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'заявка на конкурс'
        verbose_name_plural = 'заявки на конкурс'


class Vote(models.Model):
    """Абстрактная модель 'Голос' разрешающая МtM между 'Пользователем' и 'Заявкой' """
    user = models.ForeignKey(
        User,
        related_name='user_votes',
        verbose_name='пользователь',
        on_delete=models.CASCADE)

    participate = models.ForeignKey(
        'Participate',
        related_name='participate_votes',
        verbose_name='заявка')

    class Meta:
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоса'
        unique_together = ('user', 'participate')

