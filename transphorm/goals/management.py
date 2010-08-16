#!/usr/bin/env python
# encoding: utf-8

from django.db.models.signals import post_save, pre_save, post_delete
from transphorm.goals.models import ActionEntry, RewardClaim, Comment

def action_post_save(sender, **kwargs):
	instance = kwargs.get('instance')
	
	if kwargs.get('created', False) == True:
		instance.plan.points += instance.points_value()
		instance.plan.points_unclaimed += instance.points_value()
		instance.plan.save()
		
	from django.core.cache import cache
	cache_key = 'chart_%s' % instance.plan.pk
	cache.delete(cache_key)
	
	print 'Deleted chart cache'
post_save.connect(action_post_save, sender = ActionEntry)

def action_post_delete(sender, **kwargs):
	instance = kwargs.get('instance')
	
	instance.plan.points -= instance.points_value()
	instance.plan.points_unclaimed -= instance.points_value()
	instance.plan.save()
	
	from django.core.cache import cache
	cache_key = 'chart_%s' % instance.plan.pk
	cache.delete(cache_key)
post_delete.connect(action_post_delete, sender = ActionEntry)

def comment_post_save(sender, **kwargs):
	if kwargs.get('created', False) == True:
		instance = kwargs.get('instance')
		if not instance.is_spam:
			from django.core.mail import send_mail
			from django.conf import settings
			from django.template.loader import render_to_string
			from django.contrib.sites.models import Site
			
			print 'Emailing ' + instance.plan.user.email
			send_mail(
				'Someone has commented on your progress',
				render_to_string(
					'plan/email/comment.txt',
					{
						'plan': instance.plan,
						'user': instance.plan.user,
						'site': Site.objects.get_current(),
						'comment': instance
					}
				),
				getattr(settings, 'DEFAULT_FROM_EMAIL'),
				(instance.plan.user.email,),
			)
post_save.connect(comment_post_save, sender = Comment)

def claim_post_save(sender, **kwargs):
	instance = kwargs.get('instance')
	
	if kwargs.get('created', False) == True:
		instance.plan.points_unclaimed -= instance.points_value()
		instance.plan.save()

def claim_post_delete(sender, **kwargs):
	instance = kwargs.get('instance')
	
	instance.plan.points_unclaimed += instance.points_value()
	instance.plan.save()

post_save.connect(claim_post_save, sender = RewardClaim)
post_delete.connect(claim_post_delete, sender = RewardClaim)