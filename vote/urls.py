from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from mezzanine.pages import views as pages_view

urlpatterns = [
    # url(r'^$', pages_view.page, {'slug': 'competition'}, name='home'),
    url('^participate/$', views.participates_in_competition, name='participates_in_competition'),
    url('^participate/(?P<participate_id>[0-9]+)$', views.about_participate, name='about_participate'),
    url('^participate_add/$', views.participate_add, name='participate_add'),
    url('^participate_edit/$', views.participate_edit, name='participate_edit'),
    url('^competition_add/$', views.competition_add, name='competition_add'),
    url('^competition_edit/$', views.competition_edit, name='competition_edit'),
    url('^$', views.competition_list, name='competitions'),
    url('^competition/(?P<competition_id>[0-9]+)$', views.about_competition, name='about_competition'),
    url('^vote/(\d)$', views.vote, name='vote'),
    # url('^log_in/$', views.log_in, name='log_in'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'vote/registration/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'vote/registration/logout.html'}, name='logout'),
    url(r'^register/', views.register, name='register'),
]
