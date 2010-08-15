#!/usr/bin/env python
# encoding: utf-8

from django.db import models

class GoalManager(models.Manager):
	def most_popular(self):
		return self.annotate(
			plan_count = models.Count('plans')
		).order_by(
			'-plan_count'
		)

class LogEntryManager(models.Manager):
	def not_spam(self):
		q = models.Q(comment__isnull = True) | models.Q(comment__is_spam = False)
		return self.filter(q)
	
	def approved(self):
		q = models.Q(comment__isnull = True) | models.Q(comment__is_approved = True)
		return self.not_spam().filter(q)

class RewardManager(models.Manager):
	def unclaimed(self, user):
		unclaimed_points = user.plans.filter(live = True).aggregate(
			unclaimed_points = models.Sum('points_unclaimed')
		)['unclaimed_points']
		
		unclaimed_points = unclaimed_points or 0
		
		return self.filter(
			points__lte = unclaimed_points,
			plan__live = True
		)