#!/usr/bin/env python
# encoding: utf-8

from transphorm.goals.models import Goal, Plan
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

def goal_view():
	def decorator(func):
		def inner_decorator(request, *args, **kwargs):
			try:
				if len(args) >= 1:
					slug = args.pop(0)
				else:
					slug = kwargs.pop('goal')
				
				goal = Goal.objects.get(slug = slug)
				return func(request, goal, *args, **kwargs)
			except Goal.DoesNotExist:
				return HttpResponseRedirect(
					'%s?name=%s' % (
						reverse('new_goal'), args[0].replace('-', ' ')
					)
				)
		return inner_decorator
	return decorator

def plan_view(*args, **kwargs):
	def decorator(func):
		def get_outer_arg(name, default = None):
			return kwargs.get(name, default)
		
		def inner_decorator(request, *args, **kwargs):
			edit = get_outer_arg('edit')
			detail = get_outer_arg('detail')
			
			try:
				if len(args) >= 1:
					slug = args.pop(0)
				else:
					slug = kwargs.pop('goal')
				
				goal = Goal.objects.get(slug = slug)
				try:
					if len(args) > 1 and not args[1] is None:
						user = get_object_or_404(
							User, username = args.pop(1)
						)
					elif 'username' in kwargs:
						user = get_object_or_404(
							User, username = kwargs.pop('username')
						)
					elif request.user.is_authenticated():
						user = request.user
						edit = True
					else:
						return HttpResponseRedirect(
							reverse('start_plan', args = [slug])
						)
					
					plan = goal.plans.filter(
						live = True, user = user
					).latest()
					
					# Prepare to redirect if the user viewing the plan is
					# the user who created it
					
					if not detail:
						redirect = request.user.is_authenticated() and not edit
					else:
						redirect = False
					
					if redirect and plan.user == request.user:
						return HttpResponseRedirect(
							reverse('plan_logbook', args = [plan.goal.slug])
						)
					
					return func(request, goal, plan, *args, **kwargs)
				except Plan.DoesNotExist:
					try:
						if edit:
							return HttpResponseRedirect(
								reverse('start_plan', args = [goal.slug])
							)
					except UnboundLocalError:
						pass
					
					return render_to_response(
						'plan/not-attempting.html',
						{
							'user': user,
							'live_plans': user.plans.filter(live = True)
						},
						RequestContext(request)
					)
			except Goal.DoesNotExist:
				return HttpResponseRedirect(
					'%s?name=%s' % (
						reverse('new_goal'),
						slug.replace('-', ' ')
					)
				)
		return inner_decorator
	return decorator