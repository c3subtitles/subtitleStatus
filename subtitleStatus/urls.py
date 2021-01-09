from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^', include('www.urls')),
    url(r'^', include('account.urls')),
]
