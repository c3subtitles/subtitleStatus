from django.conf.urls import include, url
from django.conf.urls.static import static
from . import views
from django.urls import reverse_lazy
from django.contrib.staticfiles.views import serve
from django.conf import settings
from django.contrib import admin

urlpatterns = [
        url(r'^$', views.start, name='home'),
        url(r'^hello/$', views.clock),
        url(r'^event/(?P<acronym>(\w|-)+)/$', views.event, name='event'),
        url(r'^event/(?P<acronym>(\w|-)+)/day/(?P<day>\d+)$', views.event, name='event'),
        url(r'^event/(?P<acronym>(\w|-)+)/day/(?P<day>\d+)/lang/(?P<language>\w+)$', views.event, name='event'),
        url(r'^talk/(?P<id>\d+)/$', views.talk, name='talk'),
        url(r'^talk/frab-id/(?P<frab_id>\d+)/$', views.talk_by_frab),
        url(r'^talk/guid/(?P<guid>[0-9a-zA-Z_-]+)/$', views.talk_by_guid),
        url(r'^talk/subtitle/(?P<subtitle_id>[0-9]+)/$', views.talk_by_subtitle),
        url(r'^subtitle/(?P<id>\d+)/$', views.updateSubtitle, name='subtitle'),
        url(r'^speaker/(?P<speaker_id>\d+)/$', views.speaker, name="speaker"),
        url(r'^clock/$',views.clock),
        #url(r'^logo', views.eventLogo),
        #url(r'^', views.eventStatus),
        url(r'^statistics/talks/$',views.statistics_talks),
        url(r'^statistics/speakers/$',views.statistics_speakers),
        url(r'^statistics/speakers_in_talks/$',views.statistics_speakers_in_talks),
        url(r'^workflow/transforms/(?P<subtitle_id>[0-9]+)/(?P<next_ids>[0-9]+(,[0-9]+)*)?$', views.text_transforms_dwim, name='workflowTransforms'),
        url(r'^media_export(/((?P<timestamp>[0-9:.TZ+-]+)/?)?)?$',views.media_export),
        url(r'^test/$',views.test),
        url(r'^b_test/$',views.b_test),
        path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve),
    ]
