#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'home.html'
		}
	),
)

if getattr(settings, 'DEBUG', False):
	urlpatterns += patterns('django.views.static',
		(r'^media/(?P<path>.*)$', 'serve',
			{
				'document_root': getattr(settings, 'MEDIA_ROOT')
			}
		)
	)