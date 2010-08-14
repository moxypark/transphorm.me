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
	url(r'^start/$', 'transphorm.goals.views.start', name = 'start'),
	url(r'^new/start/$', 'transphorm.goals.views.new_goal', name = 'new_goal'),
	url(r'^(?P<goal>[\w-]+)/start/$', 'transphorm.goals.views.start_plan', name = 'start_plan'),
	url(r'^(?P<username>[\w-]+)(?P<goal>[\w-]+)/start/$', 'transphorm.goals.views.copy_plan', name = 'copy_plan'),
)

if getattr(settings, 'DEBUG', False):
	urlpatterns += patterns('django.views.static',
		(r'^media/(?P<path>.*)$', 'serve',
			{
				'document_root': getattr(settings, 'MEDIA_ROOT')
			}
		)
	)