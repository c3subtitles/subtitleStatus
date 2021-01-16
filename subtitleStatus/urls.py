from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.finders import BaseFinder
from django.contrib.staticfiles.storage import staticfiles_storage


class StaticRootFinder(BaseFinder):
    """In Debug mode, also serve files from the root static directory."""
    def find(self, path, all=False):
        full_path = staticfiles_storage.path(path)
        if staticfiles_storage.exists(full_path):
            return [full_path] if all else full_path
        return []

    def list(self, ignore_patterns):
        return iter(())


admin.autodiscover()


urlpatterns = [
    path('', include('www.urls')),
    path('accounts/', include(('django.contrib.auth.urls', 'django.contrib.auth'), 'auth')),
]
