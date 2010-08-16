#!/usr/bin/env python
# encoding: utf-8

from os import path

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'transphorm',
		'USER': 'transphorm',
		'PASSWORD': 'iy4gkbV7JPwe40hj',
		'HOST': '',
		'PORT': '',
	}
}

DEBUG = True
SITE_ROOT = path.abspath(path.dirname(__file__) + '/../')