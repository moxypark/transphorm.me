#!/usr/bin/env python
# encoding: utf-8

from os import path

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'transphorm',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

DEBUG = True
SITE_ROOT = path.abspath(path.dirname(__file__) + '/../')