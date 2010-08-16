#!/usr/bin/env python
# encoding: utf-8

def goals(request):
	from transphorm.goals.models import Plan, Profile, Reward, LogEntry
	from transphorm.goals.forms import StartForm
	from django.db.models import Q
	
	context = {
		'latest_plans': Plan.objects.filter(
			Q(user__profile__public = True) | Q(user__profile__isnull = True)
		).filter(live = True)[:5],
		
		'start_form': StartForm(),
		
		'latest_log_entries': LogEntry.objects.filter(
			Q(plan__user__profile__public = True) | Q(plan__user__profile__isnull = True)
		).filter(plan__live = True)[:10]
	}
	
	if request.GET.get('msg'):
		context['anonymous_messages'] = [request.GET.get('msg')]
	
	if request.user.is_authenticated():
		context['user_plans'] = request.user.plans.filter(live = True)
		
		try:
			context['profile'] = request.user.get_profile()
		except Profile.DoesNotExist:
			pass
		
		context['unclaimed_rewards'] = Reward.objects.unclaimed(
			request.user
		)
	
	return context