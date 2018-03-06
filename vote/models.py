from django.db import models, IntegrityError
from mezzanine.pages.models import Page, RichText
from mezzanine.core.fields import RichTextField
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericRelation
from hitcount.models import HitCountMixin, HitCount
from django import forms

COMPETITION_TYPE = (
    (1, 'Фотоконкурс'),
    (2, 'Литературный конкурс'),
    (3, 'Видеоконкурс'),
    (4, 'Аудиоконкурс'),
)


class Profile(models.Model):
    """Расширили стандартную пользовательскую модель"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField('номер телефона', max_length=15, null=True, blank=True)
    location = models.CharField('город', max_length=30, blank=True)
    birth_date = models.DateField('дата рождения', null=True, blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.get_full_name()


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
    survey_date = models.DateTimeField('опрос с', default=timezone.now() + timezone.timedelta(days=5))
    comp_type = models.IntegerField('тип конкурса', default=1, choices=COMPETITION_TYPE)
    rules = RichTextField('правила', max_length=2000)
    short_description = models.TextField('краткое описание', max_length=500)
    creator = models.ForeignKey(User, verbose_name='автор',
                                related_name='competition_user',
                                on_delete=models.CASCADE)
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')

    class Meta:
        verbose_name = 'конкурс'
        verbose_name_plural = 'конкурсы'

    @property
    def type_str(self):
        return dict(COMPETITION_TYPE)[self.comp_type]


class Participate(Page):
    """Модель заявки на участие"""
    comment = models.TextField('комментарий')
    competition_id = models.ForeignKey('Competition', verbose_name='конкурс',
                                       related_name='competition_participates',
                                       on_delete=models.CASCADE)
    content = models.FileField('файл', upload_to='uploads/', blank=True)
    creator = models.ForeignKey(User, verbose_name='автор',
                                related_name='user_participates',
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'заявка на конкурс'
        verbose_name_plural = 'заявки на конкурс'


class Vote(models.Model):
    """Абстрактная модель 'Голос' разрешающая МtM между 'Пользователем' и 'Заявкой' """
    user = models.ForeignKey(User, related_name='user_votes', verbose_name='пользователь', on_delete=models.CASCADE)
    participate = models.ForeignKey('Participate', related_name='participate_votes', verbose_name='заявка')

    class Meta:
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоса'
        unique_together = ('user', 'participate')

