from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wwwsubs.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^account/', include('account.urls')),
    url(r'^(?P<event>\w+)/', include('www.urls')),
)
