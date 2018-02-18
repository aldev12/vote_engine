# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-18 11:55
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import hitcount.models
import mezzanine.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0003_auto_20150527_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pages.Page')),
                ('survey_date', models.DateTimeField(default=datetime.datetime(2018, 2, 23, 11, 55, 52, 415534, tzinfo=utc), verbose_name='опрос с')),
                ('comp_type', models.IntegerField(choices=[(1, 'Фотоконкурс'), (2, 'Литературный конкурс'), (3, 'Видеоконкурс'), (4, 'Аудиоконкурс')], default=1, verbose_name='тип конкурса')),
                ('rules', mezzanine.core.fields.RichTextField(max_length=2000, verbose_name='правила')),
                ('short_description', models.TextField(max_length=500, verbose_name='краткое описание')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competition_user', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
            ],
            options={
                'verbose_name_plural': 'конкурсы',
                'verbose_name': 'конкурс',
                'ordering': ('_order',),
            },
            bases=('pages.page', hitcount.models.HitCountMixin),
        ),
        migrations.CreateModel(
            name='Participate',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pages.Page')),
                ('comment', models.TextField(verbose_name='комментарий')),
                ('content', models.FileField(blank=True, upload_to='documents/', verbose_name='файл')),
                ('competition_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competition_participates', to='vote.Competition', verbose_name='конкурс')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_participates', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
            ],
            options={
                'verbose_name_plural': 'заявки на конкурс',
                'verbose_name': 'заявка на конкурс',
                'ordering': ('_order',),
            },
            bases=('pages.page',),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=15, null=True, verbose_name='номер телефона')),
                ('location', models.CharField(blank=True, max_length=30, verbose_name='город')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='дата рождения')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Профили',
                'verbose_name': 'Профиль',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participate_votes', to='vote.Participate', verbose_name='заявка')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_votes', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name_plural': 'Голоса',
                'verbose_name': 'Голос',
            },
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'participate')]),
        ),
    ]
