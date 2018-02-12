from django.conf.urls import url
from . import views

urlpatterns = [
    url('^participate/$', views.participates_in_competition, name='participates_in_competition'),
    url('^competition_add/$', views.competition_add, name='competition_add'),
    url('^about_participate/$', views.about_participate, name='about_participate'),
    url('^participate_add/$', views.participate_add, name='participate_add'),
    url('^log_in/$', views.log_in, name='log_in'),
    url('^$', views.competition_list, name='competitions'),
]
