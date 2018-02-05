from django.conf.urls import url
from . import views

urlpatterns = [
    url('^participate/$', views.participates_in_competition,
        name='participates_in_competition'),
    url('^competition_add/$', views.competition_add, name='competition_add'),
    url('^$', views.competition_list),
]
