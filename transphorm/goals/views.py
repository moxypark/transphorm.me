#!/usr/bin/env python
# encoding: utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from transphorm.goals.forms import ProfileForm, StartForm, PlanForm, GoalForm, SignupForm, ActionFormSet, RewardFormSet, MilestoneFormSet
from transphorm.goals.models import Profile, Goal, Plan

GREETINGS = (
	'Good to have you back, <span>%s</span>!',
	'How are you getting on, <span>%s</span>?',
	'You&rsquo;re looking well, <span>%s</span>!',
)

def start(request):
	start_form = StartForm(request.POST)
	
	if request.method == 'GET':
		return HttpResponseRedirect('/')
	
	forms = []
	
	if request.user.is_anonymous():
		forms.append(
			SignupForm(prefix = 'signup')
		)
	
	if start_form.is_valid():
		if start_form.cleaned_data.get('plan_copy'):
			goal = start_form.cleaned_data['plan_copy']
			
			action = reverse(
				'start_plan', args = [goal.slug]
			)
			
			if request.user.is_authenticated():
				return HttpResponseRedirect(action)
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

	if request.method == 'GET' and not request.GET.get('name'):
		return HttpResponseRedirect('/')
	
	if request.method == 'POST':
		goal_form = GoalForm(request.POST, prefix = 'goal')
	else:
		goal_form = GoalForm(
			instance = Goal(name = request.GET.get('name')),
			prefix = 'goal'
		)
	
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
		
		request.user.message_set.create(
			message = 'Your goal has been created.'
		)
		
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
	try:
		goal = Goal.objects.get(slug = goal)
	except Goal.DoesNotExist:
		return HttpResponseRedirect(
			reverse('new_goal') + '?name=%s' % goal.replace('-', ' ')
		)
	
	if request.user.is_anonymous():
		if request.method == 'GET':
			signup_form = SignupForm(prefix = 'signup')
			return render_to_response(
				'start.html',
				{
					'forms': [signup_form],
					'goal': goal
				},
				RequestContext(request)
			)
		else:
			signup_form = SignupForm(request.POST, prefix = 'signup')
			
			if signup_form.is_valid():
				profile = signup_form.save()
				request.user.message_set.create(
					message = 'Your account has been created.'
				)
				
				from django.contrib.auth import login
				login(request, profile.user)
			else:
				return render_to_response(
					'start.html',
					{
						'forms': [signup_form],
						'goal': goal
					},
					RequestContext(request)
				)
	
	if goal.plans.filter(user = request.user, live = True).count() > 0:
		if request.method == 'POST' and request.POST.get('next'):
			return HttpResponseRedirect(
				request.POST.get('next')
			)
		else:
			return HttpResponseRedirect(
				reverse('edit_plan', args = [goal.slug])
			)
		
	plan = Plan(
		goal = goal,
		user = request.user
	)
	
	if request.method == 'GET':
		form = PlanForm(instance = plan)
	else:
		form = PlanForm(request.POST, instance = plan)
		if form.is_valid():
			plan = form.save()
			request.user.message_set.create(
				message = 'Your plan has been created.'
			)
			
			return HttpResponseRedirect(
				request.POST.get('next')
			)
	
	return render_to_response(
		'plan/edit.html',
		{
			'forms': [form],
			'goal': goal,
			'plan': plan,
			'next': reverse(
				'actions_edit',
				args = [plan.goal.slug]
			)
		},
		RequestContext(request)
	)

@login_required
def profile(request):
	try:
		profile = request.user.get_profile()
	except Profile.DoesNotExist:
		profile = Profile(user = request.user)
	
	if request.method == 'GET':
		form = ProfileForm(instance = profile)
	else:
		form = ProfileForm(request.POST, instance = profile)
		if form.is_valid():
			profile = form.save()
			request.user.message_set.create(
				message = 'Your profile has been updated.'
			)
	
	import random
	rnd = random.randrange(0, len(GREETINGS))
	if not 'greeting' in request.session:
		greeting = GREETINGS[rnd] % request.user.first_name or request.user.username
		request.session['greeting'] = greeting
		request.session.modified = True
	else:
		greeting = request.session['greeting']
	
	return render_to_response(
		'profile.html',
		{
			'profile_form': form,
			'greeting': greeting
		},
		RequestContext(request)
	)

@login_required
def edit_plan(request, goal):
	try:
		goal = Goal.objects.get(slug = goal)
	except Goal.DoesNotExist:
		return HttpResponseRedirect(
			reverse('new_goal') + '?name=%s' % goal.replace('-', ' ')
		)
	
	try:
		plan = goal.plans.filter(user = request.user).latest()
	except Plan.DoesNotExist:
		return HttpResponseRedirect(
			reverse('start_plan', args = [goal.slug])
		)
	
	if request.method == 'GET':
		form = PlanForm(instance = plan)
	else:
		form = PlanForm(request.POST, instance = plan)
		if form.is_valid():
			plan = form.save()
			request.user.message_set.create(
				message = 'Your plan has been updated.'
			)
			
			from django.conf import settings
			return HttpResponseRedirect(
				request.POST.get('next',
					getattr(settings, 'LOGIN_REDIRECT_URL')
				)
			)
	
	return render_to_response(
		'plan/edit.html',
		{
			'forms': [form],
			'goal': goal,
			'plan': plan
		},
		RequestContext(request)
	)

@login_required
def actions_edit(request, goal):
	goal = get_object_or_404(
		Goal, slug = goal
	)
	
	try:
		plan = goal.plans.filter(user = request.user).latest()
	except Plan.DoesNotExist:
		return HttpResponseRedirect(
			reverse('start_plan', args = [goal.slug])
		)
	
	is_wizard = False
	if plan.actions.count() == 0:
		next = reverse('rewards_edit', args = [goal.slug])
		is_wizard = True
	else:
		next = request.REQUEST.get(
			'next', reverse('edit_plan', args = [goal.slug])
		)
	
	if request.method == 'GET':
		formset = ActionFormSet(plan = plan)
	else:
		formset = ActionFormSet(request.POST, plan = plan)
		
		if formset.is_valid():
			formset.save()
			
			if 'continue' in request.POST:
				request.user.message_set.create(
					message = 'Actions for this plan have been updated.'
				)
				
				return HttpResponseRedirect(next)
			else:
				formset = ActionFormSet(plan = plan)
	
	return render_to_response(
		'plan/actions.html',
		{
			'goal': goal,
			'plan': plan,
			'formset': formset,
			'next': next,
			'is_wizard': is_wizard
		},
		RequestContext(request)
	)

@login_required
def rewards_edit(request, goal):
	goal = get_object_or_404(
		Goal, slug = goal
	)
	
	try:
		plan = goal.plans.filter(user = request.user).latest()
	except Plan.DoesNotExist:
		return HttpResponseRedirect(
			reverse('start_plan', args = [goal.slug])
		)
	
	is_wizard = False
	if plan.rewards.count() == 0:
		is_wizard = True
		next = request.REQUEST.get(
			'next', reverse('milestones_edit', args = [goal.slug])
		)
	else:
		next = request.REQUEST.get(
			'next', reverse('edit_plan', args = [goal.slug])
		)
	
	if request.method == 'GET':
		formset = RewardFormSet(plan = plan)
	else:
		formset = RewardFormSet(request.POST, plan = plan)
		
		if formset.is_valid():
			formset.save()
			
			if 'continue' in request.POST:
				request.user.message_set.create(
					message = 'Rewards for this plan have been updated.'
				)
				
				return HttpResponseRedirect(next)
			else:
				formset = RewardFormSet(plan = plan)

	return render_to_response(
		'plan/rewards.html',
		{
			'goal': goal,
			'plan': plan,
			'formset': formset,
			'next': next,
			'is_wizard': is_wizard
		},
		RequestContext(request)
	)

@login_required
def milestones_edit(request, goal):
	goal = get_object_or_404(
		Goal, slug = goal
	)
	
	try:
		plan = goal.plans.filter(user = request.user).latest()
	except Plan.DoesNotExist:
		return HttpResponseRedirect(
			reverse('start_plan', args = [goal.slug])
		)
	
	is_wizard = False
	if plan.milestones.count() == 0:
		is_wizard = True
	
	next = request.REQUEST.get(
		'next', reverse('edit_plan', args = [goal.slug])
	)
	
	if request.method == 'GET':
		formset = MilestoneFormSet(plan = plan)
	else:
		formset = MilestoneFormSet(request.POST, plan = plan)
		
		if formset.is_valid():
			formset.save()
			
			if 'continue' in request.POST:
				request.user.message_set.create(
					message = 'Milestones for this plan have been updated.'
				)
				
				return HttpResponseRedirect(next)
			else:
				formset = MilestoneFormSet(plan = plan)
	
	return render_to_response(
		'plan/milestones.html',
		{
			'goal': goal,
			'plan': plan,
			'formset': formset,
			'next': next,
			'is_wizard': is_wizard
		},
		RequestContext(request)
	)