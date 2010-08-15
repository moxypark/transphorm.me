#!/usr/bin/env python
# encoding: utf-8

from django.template import Library

register = Library()
@register.filter(name = 'model_name')
def model_name(value):
	from django.contrib.contenttypes.models import ContentType
	
	content_type = ContentType.objects.get_for_model(value)
	return content_type.model

@register.filter(name = 'model_name_verbose')
def model_name_verbose(value):
	model_class = value._meta
	return model_class.verbose_name

@register.filter(name = 'model_name_plural')
def model_name_plural(value):
	model_class = value._meta
	
	return model_class.verbose_name_plural

@register.filter(name = 'content_type_id')
def content_type_id(value):
	from django.contrib.contenttypes.models import ContentType
	
	content_type = ContentType.objects.get_for_model(value)
	return content_type.pk