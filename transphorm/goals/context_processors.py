#!/usr/bin/env python
# encoding: utf-8

def goals(request):
	from transphorm.goals.models import Plan, Profile, Reward
	from transphorm.goals.forms import StartForm
	
	context = {
		'latest_plans': Plan.objects.filter(
			user__profile__public = True,
			live = True
		)[:5],
		'start_form': StartForm()
	}
	
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