#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from transphorm.goals.managers import GoalManager, RewardManager, \
	LogEntryManager
from datetime import date, datetime, timedelta

POINT_CHOICES = tuple([(x, str(x)) for x in range(-100, 110, 10)])
AVAILABLE_POINT_CHOICES = tuple([(x, str(x)) for x in range(10, 10100, 100)])
MEASUREMENTS = (
	('in', 'inch', 'inches', 'inches'),
	('yd', 'yard', 'yards', 'yards'),
	('mi', 'mile', 'miles', 'miles'),
	('m', 'metre', 'metres', 'metres'),
	('km', 'kilometer', 'kilometers', 'kilometers'),
	('lb', 'pound', 'pounds', 'pounds'),
	('st', 'stone', 'stone', 'stone'),
	('kg', 'kilogram', 'kilograms', 'kilograms'),
	('n', 'minute', 'minutes', 'minutes'),
	('h', 'hour', 'hours', 'hours'),
	('d', 'day', 'days', 'days'),
	('it', 'item', 'items', 'how many?'),
)

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
	
	def live_plans(self):
		return self.user.plans.filter(live = True)
	
	def __unicode__(self):
		return self.user.get_full_name() or self.user.username
	
	class Meta:
		ordering = ('-user__date_joined',)

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
	
	def original_plan(self):
		return self.plans.get(original__isnull = True, live = True)
	
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
	
	points = models.IntegerField(editable = False, default = 0)
	points_unclaimed = models.PositiveIntegerField(
		editable = False, default = 0
	)
	
	def __unicode__(self):
		return u'%s wants to %s' % (self.user, self.goal.name)
	
	@models.permalink
	def get_absolute_url(self):
		return (
			'user_plan_logbook',
			[self.goal.slug, self.user.username]
		)
	
	def copy_to(self, dest_plan):
		if dest_plan.goal != self.goal:
			raise Exception('Destination goal is different from source goal')
		
		dest_plan.actions.all().delete()
		dest_plan.rewards.all().delete()
		dest_plan.milestones.all().delete()
		
		for action in self.actions.all():
			dest_plan.actions.create(
				kind = action.kind,
				name = action.name,
				measurement = action.measurement,
				points = action.points,
				description = action.description
			)
			
			print 'Copied action'
		
		for milestone in self.milestones.all():
			deadline = date.today() + timedelta(
				(
					milestone.deadline - self.started.date()
				).days
			)
			
			dest_plan.milestones.create(
				name = milestone.name,
				deadline = deadline,
				points = milestone.points
			)
			
			print 'Copied milestone'
	
	class Meta:
		ordering = ('-started',)
		get_latest_by = 'started'

class Action(models.Model):
	ACTION_TYPES = (
		('sa', 'Simple action'),
		('sc', 'Scale')
	)
	
	plan = models.ForeignKey(Plan, related_name = 'actions')
	kind = models.CharField(
		'type', max_length = 2, choices = ACTION_TYPES
	)
	
	name = models.CharField(max_length = 50, help_text = """Write in
		lowercase (eg: &ldquo;walked 1 mile today&rdquo;)"""
	)
	
	measurement = models.CharField(
		help_text = """When using a scale, the available points for this
		action can be multiplied by a value which the person attempting the
		goal types in. How is the value measured?""", max_length = 2,
		choices = tuple([(x, y) for (x, y, z, a) in MEASUREMENTS])
	)
	
	points = models.PositiveIntegerField(
		default = 10, choices = POINT_CHOICES
	)
	
	description = models.TextField(null = True, blank = True)
	
	def get_measurement_plural(self):
		for x, y, z, a in MEASUREMENTS:
			if self.measurement == x:
				return z
		
		return None
	
	def get_measurement_singular_or_plural(self, value):
		for x, y, z, a in MEASUREMENTS:
			if self.measurement == x:
				if int(value) != 1:
					return z
				else:
					return y

		return None
	
	def __unicode__(self):
		value = u'I %s' % self.name.replace(
			'[value]', 'some'
		)
		
		if self.measurement:
		 	measurement = self.get_measurement_plural()
			value = value.replace('[measurement]', measurement)
		
		return value
	
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
		to claim this reward.""", choices = AVAILABLE_POINT_CHOICES
	)
	objects = RewardManager()
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		ordering = ('points',)

class Milestone(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'milestones')
	name = models.CharField(
		max_length = 50,
		help_text = 'eg: &ldquo;First two weeks&rdquo;'
	)
	deadline = models.DateField()
	reached = models.DateTimeField(null = True, blank = True)
	points = models.IntegerField(
		'target points', choices = AVAILABLE_POINT_CHOICES,
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
		return self.deadline <= date.today()
	
	def points_remaining(self):
		return self.points - self.plan.points
	
	def will_reach(self):
		return self.points_remaining() < self.plan.points
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if self.pk:
			old = Milestone.objects.get(pk = self.pk)
			if self.deadline > old.deadline:
				self.reached = None
			
			if not old.reached:
				self.hits.create()
		
		super(Milestone, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ('deadline',)

class LogEntry(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'log_entries')
	date = models.DateTimeField(default = datetime.now())
	body = models.TextField()
	kind = models.CharField(
		max_length = 1, editable = False, choices = (
			('l', 'Comment'),
			('a', 'Action log'),
			('r', 'Reward claim'),
			('m', 'Milestone hit'),
			('c', 'Comment'),
		),
		default = 'l'
	)
	
	objects = LogEntryManager()
	
	def __init__(self, *args, **kwargs):
		super(LogEntry, self).__init__(*args, **kwargs)
	
	def __unicode__(self):
		return self.date.strftime('%Y-%m-%d, %H:%i')
	
	@models.permalink
	def get_absolute_url(self):
		return (
			'plan_logbook_entry',
			[self.plan.goal.slug, self.plan.user.username, self.pk]
		)
	
	class Meta:
		ordering = ('-date',)
		get_latest_by = 'date'
		verbose_name_plural = 'log entries'

class ActionEntry(LogEntry):
	action = models.ForeignKey(Action, related_name = 'log_entries')
	value = models.PositiveIntegerField(null = True)
	
	def __init__(self, *args, **kwargs):
		super(ActionEntry, self).__init__(*args, **kwargs)
		self.kind = 'a'
	
	def points_value(self):
		try:
			value = int(self.value)
		except (ValueError, TypeError):
			pass
		
		if self.action.kind == 'sc':
			return value * self.action.points
		else:
			return self.action.points
	
	def humanise(self, value):
		try:
			value = int(value)
		except ValueError:
			return str(value)
		
		if not 0 < value < 10:
			return str(value)
		
		return (
			'one', 'two', 'three', 'four', 'five',
			'six', 'seven', 'eight', 'nine'
		)[value - 1]
	
	def save(self, *args, **kwargs):
		if self.value and self.value > 0:
			self.body = u'I %s.' % self.action.name.replace(
				'[value]', self.humanise(self.value)
			)
			
			if self.action.measurement:
			 	measurement = self.action.get_measurement_singular_or_plural(
					self.value
				)
				
				self.body = self.body.replace('[measurement]', measurement)
		else:
			self.body = unicode(self.action)
		
		super(ActionEntry, self).save(*args, **kwargs)

class RewardClaim(LogEntry):
	reward = models.ForeignKey(Reward, related_name = 'claims')
	
	def __init__(self, *args, **kwargs):
		super(RewardClaim, self).__init__(*args, **kwargs)
		self.kind = 'r'
	
	def points_value(self):
		return self.reward.points
		
	def save(self, *args, **kwargs):
		self.plan = self.reward.plan
		
		if self.reward.name.lower()[0] in ('a', 'e', 'i', 'o', 'u'):
			vowel_letter = 'n'
		else:
			vowel_letter = ''
		
		self.body = 'I racked up %d points, and so have now claimed a%s %s as my reward.' % (
			self.reward.plan.points_unclaimed,
			vowel_letter,
			self.reward.name
		)
		
		super(RewardClaim, self).save(*args, **kwargs)

class MilestoneHit(LogEntry):
	milestone = models.ForeignKey(Milestone, related_name = 'hits')
	
	def __init__(self, *args, **kwargs):
		super(MilestoneHit, self).__init__(*args, **kwargs)
		self.kind = 'm'
	
	def save(self, *args, **kwargs):
		self.body = 'I hit my %s milestone!' % self.milestone.name
		self.plan = self.milestone.plan
		super(MilestoneHit, self).save(*args, **kwargs)

class Comment(LogEntry):
	name = models.CharField(max_length = 50)
	website = models.URLField(max_length = 255, null = True, blank = True)
	email = models.EmailField()
	is_approved = models.BooleanField()
	is_spam = models.BooleanField()
	ip = models.CharField(max_length = 20, editable = False)
	user_agent = models.CharField(max_length = 255, editable = False)
	
	def __init__(self, *args, **kwargs):
		super(Comment, self).__init__(*args, **kwargs)
		self.kind = 'c'
		
	def save(self, *args, **kwargs):
		from akismet import Akismet
		from django.conf import settings
		
		if not self.pk:
			api = Akismet(agent = 'transphorm/akismet 0.1')
			api.setAPIKey(
				getattr(settings, 'AKISMET_KEY')
			)
			
			print 'Set API key'
			
			data = {
				'comment_author': self.name,
				'comment_author_url': self.website,
				'user_ip': self.ip,
				'user_agent': self.user_agent
			}
			
			if api.comment_check(self.body, data):
				print 'Comment is SPAM'
				self.is_spam = True
			else:
				print 'Comment is NOT spam'
		
		super(Comment, self).save(*args, **kwargs)

class UserEmail(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'emails')
	subject = models.CharField(max_length = 255)
	body = models.TextField()
	date = models.DateTimeField(auto_now_add = True)
	deleted = models.BooleanField()
	kind = models.CharField(
		max_length = 2, choices = (
			('ar', 'Time to update your logbook'),
			('mr', 'A milestone reminder'),
			('mh', 'Congratulations! You hit your milestone'),
			('mm', 'Comiserations, you missed your milestone this time'),
		)
	)
	
	def __unicode__(self):
		return self.subject
	
	def save(self, *args, **kwargs):
		if not self.pk:
			self.subject = self.get_kind_display()
		
		super(UserEmail, self).save(*args, **kwargs)
	
	def prepare_message(self, site, **kwargs):
		from django.core.mail import EmailMultiAlternatives
		from django.conf import settings
		from django.template.loader import render_to_string
		
		if self.kind == 'ar':
			template = 'plan/email/action-log-reminder.txt'
		elif self.kind == 'mr':
			template = 'plan/email/milestone-reminder.txt'
		elif self.kind == 'mh':
			template = 'plan/email/milestone-hit.txt'
		elif self.kind == 'mm':
			template = 'plan/email/milestone-miss.txt'
		
		milestones = self.plan.milestones.filter(
			deadline__gt = datetime.now(),
			reached__isnull = True
		)[:1]
		
		if milestones.count() > 0:
			next_milestone = milestones[0]
		else:
			next_milestone = None
		
		unclaimed_rewards = self.plan.rewards.unclaimed(self.plan.user)
		if unclaimed_rewards.count() == 0:
			unclaimed_rewards = None
		
		context = {
			'plan': self.plan,
			'user': self.plan.user,
			'site': site,
			'unclaimed_rewards': unclaimed_rewards,
			'next_milestone': next_milestone
		}
		
		context.update(kwargs)
		
		body = render_to_string(
			template,
			context
		)
		
		html_content = render_to_string(
			'plan/email/base.html',
			{
				'body': body,
				'site': site
			}
		)
		
		message = EmailMultiAlternatives(
			self.subject,
			self.body,
			getattr(settings, 'DEFAULT_FROM_EMAIL'),
			[self.plan.user.email],
		)
		
		message.attach_alternative(
			html_content, 'text/html'
		)
		
		return message
	
	class Meta:
		ordering = ('-date',)
		get_latest_by = 'date'

from transphorm.goals.management import *