from django.conf.urls import url, include
from . import views

urlpatterns = [
	url(r'^$', views.url_list, name = "url_list"),
	url(r'^urls/(?P<pk>\d+)/$', views.url_detail, name = "url_detail"),
	url(r'^delete/(?P<pk>\d+)$', views.delete_url, ),
	url(r'^accounts/login/$', views.auth_views.login, name = "login"),
	url(r'^accounts/logout/$', views.logout_url, name = "logout"),

]