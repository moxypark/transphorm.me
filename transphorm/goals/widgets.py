#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.forms.widgets import RadioFieldRenderer

class RadioWithHelpTextFieldRenderer(forms.widgets.RadioFieldRenderer):
	def __init__(self, name, value, attrs, choices, choice_help_text):
		super(RadioWithHelpTextFieldRenderer, self).__init__(name, value, attrs, choices)
		self.choice_help_text = choice_help_text
	
	def render(self):
		from django.utils.encoding import force_unicode
		from django.utils.safestring import mark_safe
		
		return mark_safe(
			u'<ul>\n%s\n</ul>' % u'\n'.join(
				[
					u'<li>%s<span class="quiet"><br />%s</span></li>' % (
						force_unicode(w),
						self.choice_help_text[i]
					) for i, w in enumerate(self)
				]
			)
		)

class RadioSelectWithHelpText(forms.RadioSelect):
	renderer = RadioWithHelpTextFieldRenderer
	
	def __init__(self, *args, **kwargs):
		choice_help_text = kwargs.pop('choice_help_text', ())
		super(RadioSelectWithHelpText, self).__init__(*args, **kwargs)
		self.choice_help_text = choice_help_text
	
	def get_renderer(self, name, value, attrs=None, choices=()):
		if value is None:
			value = ''
		
		from django.utils.encoding import force_unicode
		from itertools import chain
		
		str_value = force_unicode(value)
		final_attrs = self.build_attrs(attrs)
		choices = list(chain(self.choices, choices))
		choice_help_text = self.choice_help_text
		return self.renderer(name, str_value, final_attrs, choices, choice_help_text)