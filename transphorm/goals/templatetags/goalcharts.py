#!/usr/bin/env python
# encoding: utf-8

from pygooglechart import SimpleLineChart
from django.template import Library
from grapefruit import Color
from django.core.cache import cache
from datetime import datetime, timedelta
from transphorm.goals.models import ActionEntry

register = Library()

@register.simple_tag
def actions_chart(plan, width = 300, height = 200, colour = '000000', labels = 'no'):
	cache_key = 'chart_%s' % plan.pk
	cached_charts = cache.get(cache_key, {})
	
	size_key = '%dx%d_%s_%s' % (width, height, colour, labels)
	cached_chart_size = cached_charts.get(size_key)
	
	if not cached_chart_size:
		print 'Adding to cache'
		today = datetime.today().date()
		end_date = today + timedelta(days = 1) - timedelta(seconds = 1)
		start_date = today - timedelta(days = 14)
		days_between = (end_date - start_date).days
	
		query = ActionEntry.objects.filter(
			plan = plan,
			date__range = (start_date, end_date)
		)
		
		dates = query.dates('date', 'day')
		
		data_dict = {}
		top_value = 0
		
		for date in dates:
			data = query.filter(
				date__year = date.year,
				date__month = date.month,
				date__day = date.day
			).values_list(
				'action__pk', 'value', 'action__points'
			)
			
			for (action_id, value, action_points) in data:
				chart_data = data_dict.get(
					action_id, {}
				)
				
				if value and int(value) > 0:
					points = value * action_points
				else:
					points = action_points
				
				key = date.date()
				total = chart_data.get(key, 0) + points
				
				if total > top_value:
					top_value = total
				
				chart_data[key] = total
				data_dict[action_id] = chart_data
		
		chart = SimpleLineChart(width, height)
		
		date_range = [
			start_date + timedelta(days = d)
			for d in range((end_date - start_date).days)
		]
		
		if labels == 'yes':
			chart.set_axis_labels(
				'x',
				[
					str(d.strftime('%d')) for d in date_range
				]
			)
		
		colours = []
		for key, data in data_dict.items():
			day_data = []
			for date in date_range:
				value = data.get(date, 0)
				day_data.append(value)
			
			chart.add_data(tuple(day_data))
		
		colours = Color.NewFromHtml(colour).TetradicScheme()
		colours = (colour,) + tuple(
			[colour.RgbToHtml(*colour.rgb)[1:] for colour in colours]
		)
		
		chart.set_colours(colours)
		cached_chart_size = '<img src="%s" alt="%s\'s %s progress chart"' % (
			chart.get_url(), plan.user.get_full_name() or plan.user.username,
			plan.goal.name
		)
		
		cached_charts[size_key] = cached_chart_size
		cache.set(cache_key, cached_charts)
	
	return cached_chart_size