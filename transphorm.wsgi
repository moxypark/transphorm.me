#!/usr/bin/env python
# encoding: utf-8

import os, sys
import django.core.handlers.wsgi

SITE_ROOT = os.path.dirname(__file__)
sys.path.insert(0, SITE_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'transphorm.settings'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(SITE_ROOT, '.python-eggs')
application = django.core.handlers.wsgi.WSGIHandler()