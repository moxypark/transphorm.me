#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('transphorm.goals.views',
	url(r'^profile/$', 'profile', name = 'profile'),
	url(r'^profile/latest/$', 'profile_latest', name = 'profile_latest'),
	url(r'^users/(?P<username>[\w-]+)/$', 'profile', name = 'user_profile'),
	url(r'^start/$', 'start', name = 'start'),
	url(r'^new/start/$', 'new_goal', name = 'new_goal'),
	url(r'^(?P<goal>[\w-]+)/$', 'plan_logbook', name = 'plan_logbook'),
	url(r'^(?P<goal>[\w-]+)/start/$', 'start_plan', name = 'start_plan'),
	url(r'^(?P<goal>[\w-]+)/log/$', 'plan_logbook_add', name = 'plan_logbook_add'),
	url(r'^(?P<goal>[\w-]+)/edit/$', 'edit_plan', name = 'edit_plan'),
	url(r'^(?P<goal>[\w-]+)/actions/$', 'actions_edit', name = 'actions_edit'),
	url(r'^(?P<goal>[\w-]+)/rewards/$', 'rewards_edit', name = 'rewards_edit'),
	url(r'^(?P<goal>[\w-]+)/rewards/(?P<id>\d+)/$', 'rewards_claim', name = 'rewards_claim'),
	url(r'^(?P<goal>[\w-]+)/rewards/(?P<id>\d+)/claim/$', 'rewards_claim', {'confirm': True}, name = 'rewards_claim_confirm'),
	url(r'^(?P<goal>[\w-]+)/milestones/$', 'milestones_edit', name = 'milestones_edit'),
	url(r'^(?P<goal>[\w-]+)/(?P<username>[\w-]+)/$', 'plan_logbook', name = 'user_plan_logbook'),
	url(r'^(?P<goal>[\w-]+)/(?P<username>[\w-]+)/(?P<id>\d+)/$', 'plan_logbook_entry', name = 'plan_logbook_entry'),
	url(r'^(?P<goal>[\w-]+)/(?P<username>[\w-]+)/(?P<id>\d+)/delete/$', 'plan_logbook_entry', {'action': 'delete'}, name = 'plan_logbook_entry_delete'),
	url(r'^(?P<goal>[\w-]+)/(?P<username>[\w-]+)/comment/$', 'plan_comment_add', name = 'plan_comment_add')
)