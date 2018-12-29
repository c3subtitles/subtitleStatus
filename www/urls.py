from django.conf.urls import patterns, include, url, static
from . import views
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.contrib import admin

urlpatterns = patterns('',
        url(r'^$', views.start, name="home"),
        url(r'^hello/$',views.clock),
        url(r'^event/(?P<event_acronym>\w+)/$', views.event),
        url(r'^event/(?P<event_acronym>\w+)/day/(?P<day>\d+)$', views.event),
        url(r'^event/(?P<event_acronym>\w+)/day/(?P<day>\d+)/lang/(?P<lang>\w+)$', views.event),
        url(r'^talk/(?P<talk_id>\d+)/$', views.talk, name="talk"),
        url(r'^talk/frab-id/(?P<frab_id>\d+)/$', views.talk_by_frab),
        url(r'^talk/guid/(?P<guid>[0-9a-zA-Z_-]+)/$', views.talk_by_guid),
        url(r'^talk/subtitle/(?P<subtitle_id>[0-9]+)/$', views.talk_by_subtitle),
        url(r'^subtitle/(?P<subtitle_id>\d+)/$', views.updateSubtitle, name="updateSub"),
        url(r'^speaker/(?P<speaker_id>\d+)/$', views.speaker, name="speaker"),
        url(r'^clock/$',views.clock),
        #url(r'^logo', views.eventLogo),
        #url(r'^', views.eventStatus),
        url(r'^statistics/talks/$',views.statistics_talks),
        url(r'^statistics/speakers/$',views.statistics_speakers),
        url(r'^statistics/speakers_in_talks/$',views.statistics_speakers_in_talks),
        url(r'^workflow/transforms/(?P<subtitle_id>[0-9]+)/(?P<next_ids>[0-9]+(,[0-9]+)*)?$', views.text_transforms_dwim, name='workflowTransforms'),
        url(r'^test/$',views.test),
        url(r'^b_test/$',views.b_test),
        url(r'^admin/',include(admin.site.urls)),
)
if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$','serve'))
