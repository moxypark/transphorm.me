#!/usr/bin/env python
# encoding: utf-8

from django import template
from django.utils.safestring import mark_safe
import hashlib

register = template.Library()

@register.filter()
def gravatar(email, size = 50):
	gravatar_url = 'http://www.gravatar.com/avatar'
	email_hash = hashlib.md5(email.lower()).hexdigest()
	
	return mark_safe(
		'%s/%s.jpg?d=identicon&s=%s' % (
			gravatar_url, email_hash, size
		)
	)