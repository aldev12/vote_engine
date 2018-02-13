from django.db import models, IntegrityError
from mezzanine.pages.models import Page, RichText
from mezzanine.core.fields import RichTextField
from django.utils import timezone

COMPETITION_TYPE = (
    (1, 'Фотоконкурс'),
    (2, 'Литературный конкурс'),
    (3, 'Видеоконкурс'),
    (4, 'Аудиоконкурс'),
)


class Competition(Page):
    Survey_date = models.DateTimeField('опрос с', default=timezone.now() + timezone.timedelta(days=5))
    Type = models.IntegerField('тип конкурса', default=1, choices=COMPETITION_TYPE)
    Rules = RichTextField('правила', max_length=2000)
    Description = models.TextField('краткое описание', max_length=500)
    Creator = models.ForeignKey('auth.User', verbose_name='автор',
                                related_name='competition_user',
                                on_delete=models.CASCADE)

    def save(self):
        if self.title and Competition.objects.filter(title=self.title).exists():
            raise IntegrityError
        super(Competition, self).save()

    class Meta:
        verbose_name = 'конкурс'
        verbose_name_plural = 'конкурсы'

    @property
    def type_str(self):
        return dict(COMPETITION_TYPE)[self.Type]


class Participate(Page):
    Comment = models.TextField('комментарий')
    competition_p = models.ForeignKey('Competition', verbose_name='конкурс',
                                      related_name='participates_competition',
                                      on_delete=models.CASCADE)
    Content = models.FileField('файл', upload_to='documents/', blank=True)
    Creator = models.ForeignKey('auth.User', verbose_name='автор',
                                related_name='participate_user',
                                on_delete=models.CASCADE)

    def save(self):
        if self.title and Participate.objects.filter(title=self.title).exists():
            raise IntegrityError
        super(Participate, self).save()

    class Meta:
        verbose_name = 'заявка на конкурс'
        verbose_name_plural = 'заявки на конкурс'


class Poll(models.Model):
    user = models.ForeignKey('auth.User', related_name='polls_user')
    participate = models.ForeignKey('Participate', related_name='polls_participate')

    class Meta:
        unique_together = ('user', 'participate')

