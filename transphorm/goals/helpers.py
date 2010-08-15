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
	return get_object_or_404(Goal, slug=slug)

def paginated(entries, request):
	from django.core.paginator import Paginator
	entries_per_page = 20
	paginator = Paginator(entries, entries_per_page)
	
	try:
		page = int(request.GET.get('page', 1))
	except ValueError:
		page = 1
	return paginator.page(page)

def serialise_actions(plan):
	from django.core import serializers
	return serializers.serialize('json', plan.actions.all())

def serialise_measurements():
	from django.utils.simplejson import dumps
	measurements = {}
	
	for (x, y, z, a,) in MEASUREMENTS:
		measurements[x] = (
			y, z, (
				a[0].upper() + a[1:]
			)
		)
	
	return dumps(measurements)