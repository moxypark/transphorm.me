#!/usr/bin/env python
# encoding: utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from transphorm.goals.forms import StartForm, PlanForm, GoalForm, SignupForm
from transphorm.goals.models import Goal, Plan

def start(request):
	start_form = StartForm(request.POST)
	
	if request.method == 'GET':
		return HttpResponseRedirect('/')
	
	from django.core.urlresolvers import reverse
	forms = []
	
	if request.user.is_anonymous():
		forms.append(
			SignupForm(prefix = 'signup')
		)
	
	if start_form.is_valid():
		if start_form.cleaned_data.get('plan_copy'):
			goal = start_form.cleaned_data['plan_copy']
			action = reverse('copy_plan', args = [goal.slug])
		else:
			goal = Goal(
				name = start_form.cleaned_data.get('plan_name')
			)
			
			action = reverse('new_goal')
			forms.append(
				GoalForm(
					instance = goal, prefix = 'goal'
				)
			)
	else:
		return render_to_response(
			'home.html',
			{
				'start_form': start_form
			},
			RequestContext(request)
		)
	
	context = {
		'goal': goal,
		'action': action
	}
	
	context['forms'] = forms
	
	return render_to_response(
		'start.html',
		context,
		RequestContext(request)
	)
	
def new_goal(request):
	forms = []
	
	if request.method == 'GET':
		return HttpResponseRedirect('/')
	
	goal_form = GoalForm(request.POST, prefix = 'goal')
	if request.user.is_anonymous():
		signup_form = SignupForm(request.POST, prefix = 'signup')
		
		if signup_form.is_valid():
			profile = signup_form.save()
			
			from django.contrib.auth import login
			login(request, profile.user)
			
			user = profile.user
		else:
			forms.append(signup_form)
			user = None
	else:
		user = request.user
	
	if not user is None and goal_form.is_valid():
		goal = goal_form.save(commit = False)	
		goal.user = user
		goal.save()
		
		from django.core.urlresolvers import reverse
		return HttpResponseRedirect(
			reverse('start_plan', args = [goal.slug])
		)
	
	forms.append(goal_form)
	
	return render_to_response(
		'start.html',
		{
			'forms': forms
		},
		RequestContext(request)
	)

def start_plan(request, goal):
	goal = get_object_or_404(
		Goal, slug = goal
	)
	
	plan = Plan(
		goal = goal,
		user = request.user
	)
	
	form = PlanForm(instance = plan)
	return render_to_response(
		'plan/edit.html',
		{
			'forms': [form],
			'goal': goal,
			'is_wizard': True
		},
		RequestContext(request)
	)

def copy_plan(request, username, goal):
	goal = get_object_or_404(
		Goal, slug = goal
	)
	
	try:
		plan = goal.plans.filter(user = request.user).latest()
	except Plan.DoesNotExist:
		raise Http404()