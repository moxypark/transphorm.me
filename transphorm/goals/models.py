#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from transphorm.goals.managers import GoalManager
from datetime import date, timedelta

class Profile(models.Model):
	GENDER_CHOICES = (
		('m', 'male'),
		('f', 'female'),	
	)
	
	user = models.ForeignKey(User, unique = True)
	dob = models.DateField('date of birth', blank = True, null = True)
	gender = models.CharField(
		max_length = 1, choices = GENDER_CHOICES,
		blank = True, null = True
	)
	about = models.TextField(blank = True, null = True)
	public = models.BooleanField('public', default = True)
	twitter = models.CharField(
		'Twitter username', max_length = 30,
		blank = True, null = True
	)
	website = models.URLField(
		'website URL', max_length = 255,
		blank = True, null = True
	)
	
	def __unicode__(self):
		return self.user.get_full_name() or self.user.username

class Goal(models.Model):
	user = models.ForeignKey(User, related_name = 'goals')
	name = models.CharField(max_length = 50)
	slug = models.CharField(
		max_length = 50, unique = True, editable = False
	)
	description = models.TextField(
		help_text = """What information let you to create this goal?
		Is there info online that could help encourage others to take up
		this goal too? (Try to keep this impersonal, so that others can
		try to achieve this goal aswell as you.)"""
	)
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
	about = models.TextField(
		null = True, blank = True, help_text = """Tell us your personal
		reasons for wanting to achieve this goal. Share as little or as
		much of yourself as you see fit, but don&rsquo;t disclose any
		proviate information."""
	)
	allow_copies = models.BooleanField(default = True)
	original = models.ForeignKey(
		'self', related_name = 'copies',
		blank = True, null = True
	)
	email_frequency = models.IntegerField(
		'frequency of emails',
		choices = (
			(0, 'Never'),
			(1, 'Every day'),
			(7, 'Every week'),
			(14, 'Every fortnight'),
			(30, 'Every 30 days')
		),
		default = 1, help_text = """Emails can be sent out which remind
		you to log your points for each day, week, etc. You can change
		this at any time, or elect never to receive emails. This does
		not affect milestone emails."""
	)
	
	def __unicode__(self):
		return u'%s wants to %s' % (self.user, self.goal.name)
	
	def copy(self, dest_user):
		raise NotImplemented('Method not implemented.')
	
	class Meta:
		ordering = ('-started',)
		get_latest_by = 'started'

class Action(models.Model):
	ACTION_TYPES = (
		('pa', 'Positive act'),
		('pi', 'Negative act'),
		('ps', 'Positive scale'),
		('ns', 'Negative scale')
	)
	
	plan = models.ForeignKey(Plan, related_name = 'actions')
	kind = models.CharField(
		'type', max_length = 2, choices = ACTION_TYPES
	)
	
	name = models.CharField(max_length = 50, help_text = """Write in
	lowercase (eg: &ldquo;walked 1 mile today&rdquo;)""")
	description = models.TextField(null = True, blank = True)
	points = models.PositiveIntegerField(default = 10)
	points_multiplier = models.PositiveIntegerField(
		help_text = """If applying a scale to this action, specify the
		number of points you get, depending on the value you enter in
		your log book everytime you perform this action (ie: walking
		5 miles in a week might result in a 100, so the multiplier is
		20 (20 points per mile)).<br />If using a negative scale, your
		points will be multiplied as before, but deducted from your
		total.""",
		default = 1
	)
	
	def __unicode__(self):
		return u'I %s' % self.name
	
	class Meta:
		ordering = ('points',)

class Reward(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'rewards')
	name = models.CharField(max_length = 50)
	description = models.TextField(null = True, blank = True)
	webpage = models.URLField(
		'webpage URL', null = True, blank = True,
		help_text = """If the thing you want can be bought online, put
		the address in here to easily get hold of it when you come to
		claim your reward."""
	)
	points = models.PositiveIntegerField(
		help_text = """The number of points you need to achieve in attain
		to claim this reward."""
	)
	
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
	name = models.CharField(max_length = 50, help_text = 'eg: &ldquo;First two weeks&rdquo;')
	deadline = models.DateField()
	reached = models.DateTimeField(null = True, blank = True)
	points = models.IntegerField(
		'target points',
		help_text = """The minimum number of points that should have
		been accrued since the last milestone, or since the plan was
		started."""
	)
	send_emails = models.BooleanField(
		'send reminder and progress emails',
		help_text = """You&rsquo;ll receive an email a few days before
		your milestone is due, to let you know the number of points you
		need to obtain by the given deadline.""",
		default = True
	)
	
	@property
	def past(self):
		return self.deadline < date.today()
	
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