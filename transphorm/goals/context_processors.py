#!/usr/bin/env python
# encoding: utf-8

def goals(request):
	from transphorm.goals.models import Plan
	from transphorm.goals.forms import StartForm
	
	return {
		'latest_plans': Plan.objects.all()[:5],
		'start_form': StartForm()
	}