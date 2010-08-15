#!/usr/bin/env python
# encoding: utf-8

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from transphorm.goals.forms import ProfileForm, StartForm, PlanForm, \
	GoalForm, SignupForm, ActionFormSet, RewardFormSet, MilestoneFormSet, \
	LogEntryForm, CommentForm, ActionEntryForm, RewardClaimForm

from transphorm.goals.models import Profile, Goal, Plan, LogEntry, Comment, Reward

from transphorm.goals import helpers
from transphorm.goals.decorators import *
from django.views.decorators.http import require_GET, require_POST

GREETINGS = (
	'Good to have you back, <span>%s</span>!',
	'How are you getting on, <span>%s</span>?',
	'You&rsquo;re looking well, <span>%s</span>!',
)

@require_POST
def start(request):
	"""
	Acceps POSTs carrying either a predefined Goal object or the name
	of a new goal to create.
	"""
	
	start_form = StartForm(request.POST)
	forms = []
	
	if request.user.is_anonymous():
		# If this is a new user, add a signup/login form to the page
		forms.append(
			SignupForm(prefix = 'signup')
		)
	
	# If the previous page submitted valid info, look for the plan that was
	# generated for the selected goal, or create a new goal with the name
	# specified in the post.
	
	if start_form.is_valid():
		if start_form.cleaned_data.get('plan_copy'):
			goal = start_form.cleaned_data['plan_copy']
			
			action = reverse(
				'start_plan', args = [goal.slug]
			)
			
			# If the user is already logged in, redirect them to the
			# Start Plan page so they can add the Goal to their profile.
			
			if request.user.is_authenticated():
				return HttpResponseRedirect(action)
		else:
			# Create a new Goal, and set the start page form to post to the
			# New Goal page.
			
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
		# If something wasn't submitted correctly, redisplay the homepage
		# with the errored form
		
		return render_to_response(
			'home.html',
			{
				'start_form': start_form
			},
			RequestContext(request)
		)
	
	# If all's well, display the Start page with the relevant forms
	return render_to_response(
		'start.html',
		{
			'goal': goal,
			'action': action,
			'forms': forms
		},
		RequestContext(request)
	)

def new_goal(request):
	"""
	Creates a new Goal object from either a name specified in the GET
	or the POST. If it's in the POST, we can take a few more details.
	"""
	
	forms = []
	
	# If no name was specified in the querystring, take the user
	# back to the homepage
	if request.method == 'GET' and not request.GET.get('name'):
		return HttpResponseRedirect('/')
	
	# Create a new Goal object and set it as the form instance, so we
	# can prepopulate the form
	goal = Goal(name = request.GET.get('name'))
	
	if request.method == 'POST':
		goal_form = GoalForm(request.POST, prefix = 'goal')
	else:
		goal_form = GoalForm(instance = goal, prefix = 'goal')
	
	# If the user is anonymous (as users can come to this page without
	# logging in), create a signup/login form and att that to the page
	if request.user.is_anonymous():
		signup_form = SignupForm(request.POST or None, prefix = 'signup')
		
		# Sign the user up or log him in, then remove the form from the
		# page if the form was submitted with no errors.
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
	
	# If the user is logged in, and the goal details are correct,
	# create the new Goal object and attach it to the user. Message the
	# user then take them to the Start Plan page.
	
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
	
	# If we came to this page via a GET, or the POST has invalid data,
	# (re)display the form page
	forms.append(goal_form)
	
	return render_to_response(
		'start.html',
		{
			'forms': forms,
			'goal': goal
		},
		RequestContext(request)
	)

@goal_view()
def start_plan(request, goal):
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
				profile.user.message_set.create(
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

def profile(request, username = None):
	context = {}
	
	if username:
		profile = get_object_or_404(
			Profile, user__username = username
		)
		
		if not profile.public:
			from django.conf import settings
			return HttpResponseRedirect(
				'%s?next=%s' % (
					getattr(settings, 'LOGIN_URL'), request.path
				)
			)
		
		context['profile'] = profile
		action = 'view'
	elif request.user.is_authenticated():
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

		context['profile_form'] = form
		action = 'edit'
	else:
		from django.conf import settings
		return HttpResponseRedirect(
			'%s?next=%s' % (
				getattr(settings, 'LOGIN_URL'), request.path
			)
		)
	
	return render_to_response(
		'profile/%s.html' % action,
		context,
		RequestContext(request)
	)

@login_required
@plan_view(edit = True)
def edit_plan(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	next = reverse('plan_logbook', args = [goal.slug])
	
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
				request.POST.get('next', next)
			)
	
	return render_to_response(
		'plan/edit.html',
		{
			'forms': [form],
			'goal': goal,
			'plan': plan,
			'next': next,
		},
		RequestContext(request)
	)

@login_required
@plan_view(edit = True)
def actions_edit(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	if plan.actions.count() == 0:
		next = reverse('rewards_edit', args = [goal.slug])
		is_wizard = True
	else:
		is_wizard = False
		next = request.REQUEST.get(
			'next', reverse('plan_logbook', args = [goal.slug])
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
@plan_view(edit = True)
def rewards_edit(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	is_wizard = False
	if plan.rewards.count() == 0:
		is_wizard = True
		next = request.REQUEST.get(
			'next', reverse('milestones_edit', args = [goal.slug])
		)
	else:
		next = request.REQUEST.get(
			'next', reverse('plan_logbook', args = [goal.slug])
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
@plan_view(edit = True)
def rewards_claim(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	try:
		pk = args[2]
	except IndexError:
		pk = kwargs.get('id')
	
	confirm = kwargs.get('confirm', False)
	try:
		reward = Reward.objects.unclaimed(request.user).get(pk = pk)
	except Reward.DoesNotExist:
		raise Http404('Reward not found, or already claimed')
	
	if confirm:
		reward.claims.create()
		request.user.message_set.create(
			message = 'You have claimed your reward. Well done!'
		)
		
		return HttpResponseRedirect(
			request.GET.get('next', reverse('profile_latest'))
		)
	
	return render_to_response(
		'plan/claim.html',
		{
			'reward': reward,
			'next': request.GET.get('next', request.META.get('HTTP_REFERER')),
			'unclaimed_rewards': None
		},
		RequestContext(request)
	)

@login_required
@plan_view(edit = True)
def milestones_edit(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	is_wizard = plan.milestones.count() == 0
	next = request.REQUEST.get(
		'next', reverse('plan_logbook', args = [goal.slug])
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

@plan_view()
def plan_logbook(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	forms = []
	extra_context = {}
	
	if request.user != plan.user:
		comment = Comment(plan = plan)
		if request.user.is_authenticated():
			comment.name = request.user.get_full_name() or request.user.username
			comment.email = request.user.email
			
			try:
				profile = request.user.get_profile()
				comment.website = profile.website
			except Profile.DoesNotExist:
				pass
		
		forms.append(CommentForm(instance = comment))
		action = reverse(
			'plan_comment_add', args = [
				goal.slug, plan.user.username
			]
		)
	
	elif request.user.is_authenticated():
		for form_class in (ActionEntryForm, LogEntryForm):
			forms.append(form_class())
		
		action = reverse('plan_logbook_add', args = [goal.slug])
		extra_context.update(
			{
				'actions_serialized': helpers.serialise_actions(plan),
				'measurements_serialized': helpers.serialise_measurements(),
				'greeting': helpers.get_greeting(request)
			}
		)
	else:
		return HttpResponseRedirect(
			reverse('start_plan', args = [goal])
		)
	
	entries = helpers.paginated(plan.log_entries.all(), request)
	
	if request.user != plan.user:
		try:
			profile = get_object_or_404(
				Profile, user = plan.user
			)
			
			if not profile.public:
				from django.conf import settings
				return HttpResponseRedirect(
					'%s?next=%s' % (
						getattr(settings, 'LOGIN_URL'), request.path
					)
				)
			
			user = profile.user
			if profile.gender == 'm':
				gender = 'he'
			elif profile.gender == 'f':
				gender = 'she'
			else:
				gender = 'they'
		except Profile.DoesNotExist:
			raise Http404()
	else:
		gender = None
	
	extra_context.update(
		{
			'goal': goal,
			'plan': plan,
			'forms': forms,
			'entries': entries,
			'user': plan.user,
			'gender': gender,
			'action': action
		}
	)
	
	return render_to_response(
		'plan/logbook.html',
		extra_context,
		RequestContext(request)
	)

@plan_view(detail = True)
def plan_logbook_entry(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	try:
		pk = args[2]
	except IndexError:
		pk = kwargs.get('id')
	
	entry = get_object_or_404(
		LogEntry, plan = plan, pk = pk
	)
	
	action = kwargs.get('action')
	if action == 'delete':
		entry.delete()
		
		request.user.message_set.create(
			message = 'This %s has been deleted.' % entry.get_kind_display()
		)
		
		return HttpResponseRedirect(
			reverse('plan_logbook', args = [goal.slug])
		)
	
	can_delete = request.user == plan.user
	
	return render_to_response(
		'plan/entry.html',
		{
			'entry': entry,
			'greeting': helpers.get_greeting(request),
			'user': plan.user,
			'plan': plan,
			'goal': goal,
			'can_delete': can_delete
		},
		RequestContext(request)
	)

@login_required
@plan_view(edit = True)
@require_POST
def plan_logbook_add(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	for i, form_class in enumerate((ActionEntryForm, LogEntryForm)):
		if request.POST.get('form%d' % (i + 1)):
			entry = form_class._meta.model(plan = plan)
			form = form_class(request.POST, instance = entry)
			
			if form.is_valid():
				entry = form.save()
				
				request.user.message_set.create(
					message = 'Your entry has been logged.'
				)
				
				return HttpResponseRedirect(
					reverse('plan_logbook', args = [goal.slug])
				)
			else:
				return render_to_response(
					'plan/error.html',
					{
						'goal': goal,
						'user': plan.user,
						'plan': plan,
					},
					RequestContext(request)
				)
	
	return render_to_response(
		'plan/logbook.html',
		{
			'goal': goal,
			'user': plan.user,
			'plan': plan,
			'forms': forms
		},
		RequestContext(request)
	)

@plan_view()
@require_POST
def plan_comment_add(request, *args, **kwargs):
	goal = args[0]
	plan = args[1]
	
	comment = Comment(plan = plan)
	form = CommentForm(request.POST, instance = comment)
	
	if form.is_valid():
		comment = form.save()
		
		return HttpResponseRedirect(
			reverse('user_plan_logbook', args = [goal.slug, username])
		)
	
	return render_to_response(
		'plan/error.html',
		{
			'goal': goal,
			'user': plan.user,
			'plan': plan,
		},
		RequestContext(request)
	)

@login_required
def profile_latest(request):
	try:
		plan = request.user.plans.filter(
			live = True
		).latest()
		
		return HttpResponseRedirect(
			reverse('plan_logbook', args = [plan.goal.slug])
		)
	except Plan.DoesNotExist:
		return HttpResponseRedirect(
			reverse('profile')
		)