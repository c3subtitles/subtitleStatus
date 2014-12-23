from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
        url(r'^$', views.start),
        url(r'^hello/$',views.clock),
        url(r'^event/(?P<event_acronym>\w+)/$', views.event),
        url(r'^event/(?P<event_acronym>\w+)/day/(?P<day>\d+)$', views.event),
        url(r'^event/(?P<event_acronym>\w+)/day/(?P<day>\d+)/lang/(?P<lang>\w+)$', views.event),
        url(r'^talk/(?P<talk_id>\d+)/$', views.talk, name="talk"),
        url(r'^subtitle/(?P<subtitle_id>\d+)/$', views.updateSubtitle, name="updateSub"),
        url(r'^clock/$',views.clock),
        #url(r'^logo', views.eventLogo),
        #url(r'^', views.eventStatus),
)
#test
