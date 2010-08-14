#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from transphorm.goals.models import Profile, Goal, Plan, Action, Reward, Claim, Milestone, LogEntry

class ProfileAdmin(admin.ModelAdmin):
	list_display = (
		'__unicode__', 'gender', 'dob', 'public', 'twitter', 'website'
	)
	
	list_filter = (
		'gender', 'public'
	)
	
	date_hierarchy = 'dob'

class GoalAdmin(admin.ModelAdmin):
	list_display = ('user', 'name', 'slug', 'has_deadline', 'live')
	list_filter = ('live',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(Plan)
admin.site.register(Action)
admin.site.register(Reward)
admin.site.register(Milestone)