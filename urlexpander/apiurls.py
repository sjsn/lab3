from django.conf.urls import url, include
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

# api urls (start with api/)
urlpatterns = [
	url(r'^urls/$', views.list_urls),
	url(r'^urls/(?P<pk>[0-9]+)$', views.detail_url),
]

urlpatterns = format_suffix_patterns(urlpatterns)
