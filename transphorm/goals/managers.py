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