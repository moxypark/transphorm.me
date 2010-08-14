#!/usr/bin/env python
# encoding: utf-8

def goals(request):
	from transphorm.goals.models import Plan
	from transphorm.goals.forms import StartForm
	
	context = {
		'latest_plans': Plan.objects.all()[:5],
		'start_form': StartForm()
	}
	
	if request.user.is_authenticated():
		context['user_plans'] = request.user.plans.filter(live = True)
	
	return context