from django.urls import path, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('', include('www.urls')),
    path('accounts/', include(('django.contrib.auth.urls', 'django.contrib.auth'), 'auth')),
]
