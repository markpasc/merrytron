from django.conf.urls import patterns, url

from holiday import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
)
