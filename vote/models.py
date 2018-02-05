from django.db import models
from mezzanine.pages.models import Page
from django.utils import timezone

COMPETITION_TYPE = (
    (1, 'Фотоконкурс'),
    (2, 'Литературный конкурс'),
    (3, 'Видеоконкурс'),
    (4, 'Аудиоконкурс'),
)


class Competition(Page):
    Type = models.IntegerField('тип конкурса', default=1, choices=COMPETITION_TYPE)


class Participate(Page):
    Comment = models.TextField('комментарий')
    competition_p = models.ForeignKey('Competition', verbose_name='конкурс',
                                      related_name='participates_competition',
                                      on_delete=models.CASCADE)
    Content = models.FileField('файл', upload_to='documents/')


class Poll(models.Model):
    competition = models.ForeignKey('Competition', related_name='polls_competition')
    participate = models.ForeignKey('Participate', related_name='polls_participate')

    class Meta:
        unique_together = ('competition', 'participate')