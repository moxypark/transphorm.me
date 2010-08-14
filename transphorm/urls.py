#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'home.html'
		}
	),
	url(r'^profile/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'profile.html'
		},
		name = 'profile'
	),
)

urlpatterns += patterns('django.contrib.auth.views',
	url(r'^login/$', 'login', name = 'login'),
	url(r'^logout/$', 'logout', name = 'logout'),
)

if getattr(settings, 'DEBUG', False):
	urlpatterns += patterns('django.views.static',
		(r'^media/(?P<path>.*)$', 'serve',
			{
				'document_root': getattr(settings, 'MEDIA_ROOT')
			}
		)
	)
	
urlpatterns += patterns('',
	url(r'^', include('transphorm.goals.urls')),
)