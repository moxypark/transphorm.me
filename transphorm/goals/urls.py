#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('transphorm.goals.views',
	url(r'^profile/$', 'profile', name = 'profile'),
	url(r'^start/$', 'start', name = 'start'),
	url(r'^new/start/$', 'new_goal', name = 'new_goal'),
	url(r'^(?P<goal>[\w-]+)/start/$', 'start_plan', name = 'start_plan'),
	url(r'^(?P<goal>[\w-]+)/$', 'edit_plan', name = 'edit_plan'),
	url(r'^(?P<goal>[\w-]+)/actions/$', 'actions_edit', name = 'actions_edit'),
	url(r'^(?P<goal>[\w-]+)/rewards/$', 'rewards_edit', name = 'rewards_edit'),
	url(r'^(?P<goal>[\w-]+)/milestones/$', 'milestones_edit', name = 'milestones_edit')
)