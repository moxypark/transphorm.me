#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from transphorm.goals.managers import GoalManager

class Profile(models.Model):
	GENDER_CHOICES = (
		('m', 'male'),
		('f', 'female'),	
	)
	
	user = models.ForeignKey(User, unique = True)
	dob = models.DateField('date of birth', blank = True, null = True)
	gender = models.CharField(max_length = 1, choices = GENDER_CHOICES, blank = True, null = True)
	about = models.TextField(blank = True, null = True)
	public = models.BooleanField('public', default = True)
	twitter = models.CharField('Twitter username', max_length = 30, blank = True, null = True)
	website = models.URLField('website URL', max_length = 255, blank = True, null = True)
	
	def __unicode__(self):
		return self.user.get_full_name() or self.user.username

class Goal(models.Model):
	user = models.ForeignKey(User, related_name = 'goals')
	name = models.CharField(max_length = 50)
	slug = models.CharField(max_length = 50, unique = True, editable = False)
	description = models.TextField()
	has_deadline = models.BooleanField('has a deadline')
	live = models.BooleanField(default = True)
	objects = GoalManager()
	
	def save(self, *args, **kwargs):
		if not self.slug:
			from django.template.defaultfilters import slugify
			self.slug = slugify(self.name)
		
		super(Goal, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return self.name

class Plan(models.Model):
	goal = models.ForeignKey(Goal, related_name = 'plans')
	user = models.ForeignKey(User, related_name = 'plans')
	started = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	live = models.BooleanField(default = True)
	deadline = models.DateField(null = True, blank = True)
	about = models.TextField(null = True, blank = True)
	allow_copies = models.BooleanField(default = True)
	original = models.ForeignKey('self', related_name = 'copies', blank = True, null = True)
	
	def __unicode__(self):
		return u'%s wants to %s' % (self.user, self.goal.name)
	
	def copy(self, dest_user):
		raise NotImplemented('Method not implemented.')
	
	class Meta:
		ordering = ('-started',)
		get_latest_by = 'started'

class Action(models.Model):
	ACTION_TYPES = (
		('pa', 'Action (ie: I ate cereal for breakfast)'),
		('pi', 'Inaction (ie: I did not work late last night)'),
		('ps', 'Positive scale (ie: I walked X miles this week)'),
		('ns', 'Negative scale (ie: I only smoked X times today)')
	)
	
	plan = models.ForeignKey(Plan, related_name = 'actions')
	kind = models.CharField(
		'type', max_length = 2, choices = ACTION_TYPES,
		help_text = """An action is something simple and positive,
		that has a fixed number of points.<br /><br />Inaction means
		you get points for <em>not</em> doing negative things.<br />
		<br />You can get more complex by using a positive or negative
		scale, so that the more do something positive (or don&rsquo;t
		do something negative), the more points you get."""
	)
	
	name = models.CharField(max_length = 50)
	description = models.TextField(null = True, blank = True)
	points = models.PositiveIntegerField()
	points_multiplier = models.PositiveIntegerField(
		default = 0,
		help_text = """If applying a scale to this action, specify the
		number of points you get, depending on the value you enter in
		your log book everytime you perform this action (ie: walking
		5 miles in a week might result in a 100, so the multiplier is
		20 (20 points per mile))."""
	)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('points',)

class Reward(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'rewards')
	name = models.CharField(max_length = 50)
	description = models.TextField(null = True, blank = True)
	webpage = models.URLField('webpage URL', null = True, blank = True)
	points = models.PositiveIntegerField()
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		ordering = ('points',)

class Claim(models.Model):
	reward = models.ForeignKey(Reward, related_name = 'claims')
	date = models.DateTimeField(auto_now_add = True)
	
	class Meta:
		ordering = ('-date',)
		get_latest_by = 'date'

class Milestone(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'milestones')
	name = models.CharField(max_length = 50)
	deadline = models.DateField()
	reached = models.DateTimeField(null = True, blank = True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('deadline',)

class LogEntry(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'log_entries')
	date = models.DateTimeField(auto_now_add = True)
	body = models.TextField()
	
	def __unicode__(self):
		return self.date.strftime('%Y-%m-%d, %H:%i')
	
	class Meta:
		ordering = ('-date',)
		get_latest_by = 'date'