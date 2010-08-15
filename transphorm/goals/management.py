#!/usr/bin/env python
# encoding: utf-8

from django.db.models.signals import post_save, post_delete
from transphorm.goals.models import ActionEntry, RewardClaim

def action_post_save(sender, **kwargs):
	instance = kwargs.get('instance')
	instance.plan.points += instance.points_value()
	instance.plan.points_unclaimed += instance.points_value()
	instance.plan.save()

def action_post_delete(sender, **kwargs):
	instance = kwargs.get('instance')
	instance.plan.points -= instance.points_value()
	instance.plan.points_unclaimed -= instance.points_value()
	instance.plan.save()

post_save.connect(action_post_save, sender = ActionEntry)
post_delete.connect(action_post_delete, sender = ActionEntry)

def claim_post_save(sender, **kwargs):
	instance = kwargs.get('instance')
	instance.plan.points_unclaimed -= instance.points_value()
	instance.plan.save()

def claim_post_delete(sender, **kwargs):
	instance = kwargs.get('instance')
	instance.plan.points_unclaimed += instance.points_value()
	instance.plan.save()

post_save.connect(claim_post_save, sender = RewardClaim)
post_delete.connect(claim_post_delete, sender = RewardClaim)