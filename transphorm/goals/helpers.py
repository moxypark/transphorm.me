from transphorm.goals.models import Goal, Plan, MEASUREMENTS
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import random

GREETINGS = (
	'Good to have you back, <span>%s</span>!',
	'How are you getting on, <span>%s</span>?',
	'Looking good, <span>%s</span>!'
)

def get_greeting(request):
	"""
	Returns a random greeting to the user for their Plan page. The greeting
	format is then saved into session
	"""
	
	if request.user.is_anonymous():
		return None
	
	rnd = random.randrange(0, len(GREETINGS))
	
	if 'greeting' not in request.session:
		greeting = GREETINGS[rnd]
		request.session['greeting'] = greeting
		request.session.modified = True
	else:
		greeting = request.session['greeting']
	
	name = request.user.first_name or ''
	if name == '':
		name = request.user.username
	
	return (greeting % name)

def get_goal_or_404(slug):
	"""
	Return a Goal object matching the given slug, or raise an Http404 error
	"""
	return get_object_or_404(Goal, slug = slug)

def paginated(entries, request):
	"""
	Return a paginated list of log entries
	"""
	
	from django.core.paginator import Paginator
	entries_per_page = 20
	paginator = Paginator(entries, entries_per_page)
	
	try:
		page = int(request.GET.get('page', 1))
	except ValueError:
		page = 1
	return paginator.page(page)

def serialise_actions(plan):
	"""
	Serialise the actions of a particulr plan into a JOSN string
	"""
	from django.core import serializers
	return serializers.serialize('json', plan.actions.all())

def serialise_measurements():
	"""
	Serialise the measurements for actions into a JSON string
	"""
	from django.utils.simplejson import dumps
	measurements = {}
	
	for (x, y, z, a,) in MEASUREMENTS:
		measurements[x] = (
			y, z, (
				a[0].upper() + a[1:]
			)
		)
	
	return dumps(measurements)
	
def cron(fake_date = None):
	"""
	A cron job which should run at, say 5pm every day, and give people
	updates on their progress and helpful reminders about milestones that are
	upcoming, congratulations on ones that are hit and comiserations on the
	ones that have been missed.
	
	All emails are logged, partly for the user's convenience but mainly so that
	hte cron job knows when it's last emailed a user so it doesn't email them
	again, unless necessary.
	"""
	
	from datetime import datetime, timedelta
	from django.core.mail import get_connection
	from django.contrib.sites.models import Site
	
	plans = Plan.objects.filter(live = True).exclude(email_frequency = 0)
	messages = []
	log = []
	now = fake_date or datetime.now()
	
	site = Site.objects.get_current()
	for plan in plans:
		can_email = False
		
		try:
			latest_email = plan.emails.latest()
			next_email_date = latest_email.date + timedelta(
				days = plan.email_frequency
			)
			
			# If the next email date is in the past, we need to email this
			# user an action reminder
			if next_email_date <= now:
				can_email = True
		except:
			can_email = True
		
		if can_email:
			email = plan.emails.create(kind = 'ar')
			messages.append(
				email.prepare_message(site)
			)
			
			log.append(
				'Prepared message for user %s: %s' % (
					plan.user.username, email.subject
				)
			)
		
		can_email = False
		
		try:
			latest_email = plan.emails.filter(kind = 'mr').latest()
			next_email_date = latest_email.date + timedelta(days = 5)
			
			# If 5 days have passed since the last email, we can prepare to
			# send milestone reminders
			if next_email_date <= now:
				can_email = True
		except:
			# No milestone reminders have been sent before. All clear
			can_email = True
		
		if can_email:
			upcoming_milestones = plan.milestones.filter(
				deadline__range = (
					now, now + timedelta(days = 3)
				),
				reached__isnull = True,
				send_emails = True
			)
		
			for milestone in upcoming_milestones:
				email = plan.emails.create(kind = 'mr')
				messages.append(
					email.prepare_message(site, milestone = milestone)
				)
				
				log.append(
					'Prepared milestone reminder for user %s: %s' % (
						plan.user.username, email.subject
					)
				)
		
		milestones_today = plan.milestones.filter(
			deadline__year = now.year,
			deadline__month = now.month,
			deadline__day = now.day,
			reached__isnull = True,
			send_emails = True
		)
		
		for milestone in milestones_today:
			if milestone.points_remaining() > 0:
				email = plan.emails.create(kind = 'mm')
			else:
				milestone.reached = now
				milestone.save()
				email = plan.emails.create(kind = 'mh')
			
			messages.append(
				email.prepare_message(site, milestone = milestone)
			)
			
			log.append(
				'Prepared milestone notification for user %s: %s' % (
					plan.user.username, email.subject
				)
			)
	
	connection = get_connection()
	connection.send_messages(messages)
	
	return log