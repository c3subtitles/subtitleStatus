from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
        url(r'css', views.eventCSS),
        url(r'^logo', views.eventLogo),
        url(r'^', views.eventStatus),
)
