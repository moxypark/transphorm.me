#!/usr/bin/env python
# encoding: utf-8

from settings_local import *
from os import path

TEMPLATE_DEBUG = DEBUG

ADMINS = (
	('Moxy Park', 'moxypark@me.com'),
)

MANAGERS = ADMINS
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
SITE_ID = 1
USE_I18N = False
USE_L10N = False
MEDIA_ROOT = path.abspath(path.join(SITE_ROOT, 'media'))
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
SECRET_KEY = 'h#^38&_-#44$70f9#bf46)s8!g91vido_(im*0dr0g#9-+x=%c'

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#	 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.transaction.TransactionMiddleware'
)

ROOT_URLCONF = 'transphorm.urls'

TEMPLATE_DIRS = (
	path.join(SITE_ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.request',
	'django.core.context_processors.media',
	'django.core.context_processors.csrf',
	'transphorm.goals.context_processors.goals'
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.admin',
	'django.contrib.humanize',
	'django.contrib.markup',
	'transphorm.goals',
	'transphorm.social'
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/latest/'
AUTH_PROFILE_MODULE = 'goals.Profile'

AKISMET_KEY = '7b729c6cada1'
DEFAULT_FROM_EMAIL = 'website@transphorm.me'