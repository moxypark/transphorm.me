#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.contrib.auth.models import User
from transphorm.goals.models import Profile, Plan, Goal

class StartForm(forms.Form):
	plan_copy = forms.ModelChoiceField(
		queryset = Goal.objects.most_popular(),
		required = False,
		empty_label = None
	)
	
	def __init__(self, *args, **kwargs):
		super(StartForm, self).__init__(*args, **kwargs)
		
		choices = [(x, y) for (x, y) in self.fields['plan_copy'].choices]
		choices.append(('', '(create a new goal)'))
		
		self.fields['plan_copy'].widget.choices = choices
		self.fields['plan_copy'].initial = choices[0][0]
	
	plan_name = forms.CharField(max_length = 50, required = False)
	
	def clean_plan_name(self):
		plan_name = self.cleaned_data.get('plan_name', None)
		if self.cleaned_data['plan_copy'] in (None, ''):
			if plan_name is None or plan_name == '':
				raise forms.ValidationError('Enter a new goal name.')
			
			from django.template.defaultfilters import slugify
			goals = Goal.objects.filter(
				slug__iexact = slugify(plan_name)
			).count()
			
			if goals > 0:
				raise forms.ValidationError('That goal already exists.')
			
		return plan_name
	
	class Media:
		js = ('js/start-form.js',)

class PlanForm(forms.ModelForm):
	live = forms.BooleanField(
		label = 'I\'m still working on this goal'
	)
	
	def __init__(self, *args, **kwargs):
		super(PlanForm, self).__init__(*args, **kwargs)
		if not self.instance.original:
			del self.fields['live']
			del self.fields['allow_copies']
		
		self.fields['deadline'].required = self.instance.goal.has_deadline
	
	class Meta:
		model = Plan
		exclude = (
			'goal',
			'user',
			'original'
		)

class GoalForm(forms.ModelForm):
	name = forms.CharField(
		label = 'Name your goal',
		help_text = 'It should be in lowercase. Imagine it in a sentence, starting with &ldquo;I want to...&rdquo;'
	)
	
	description = forms.CharField(
		label = 'Tell us a bit about your goal',
		help_text = 'Why is it an important goal for you and others to try and achieve?',
		widget = forms.Textarea
	)
	
	has_deadline = forms.BooleanField(
		label = 'Can people set a deadline for this goal?',
		required = False
	)
	
	def clean_name(self):
		name = self.cleaned_data['name']
		if name[0].isupper():
			raise forms.ValidationError('Please don\'t start with a capital letter.')
		
		if name.lower().startswith('i want to'):
			raise forms.ValidationError('Please don\'t start with the phrase \'I want to\'.')
		
		return name
	
	class Meta:
		model = Goal
		exclude = ('user', 'live',)

class SignupForm(forms.ModelForm):
	create_account = forms.ChoiceField(
		label = 'Are you new here?',
		choices = (
			(True, 'Yes, sign me up!'),
			(False, 'No, let me login'),
		),
		widget = forms.RadioSelect,
		initial = True
	)
	
	username = forms.RegexField(
		regex = '^[a-z0-9]+$'
	)
	
	password = forms.CharField(
		widget = forms.PasswordInput
	)
	
	password_confirm = forms.CharField(
		label = 'Confirm your password',
		widget = forms.PasswordInput
	)
	
	email = forms.EmailField(
		label = 'Email address'
	)
	
	email_confirm = forms.EmailField(
		label = 'Confirm your eemail address'
	)
	
	dob = forms.DateField(
		label = 'Date of birth',
		required = False,
		help_text = 'This is optional, and isn&rsquo;t shared with anyone'
	)
	
	gender = forms.ChoiceField(
		label = 'Are you male or female?',
		choices = (
			('m', 'Male'),
			('f', 'Female'),
			('', 'None of your business!')
		),
		required = False,
		widget = forms.RadioSelect,
		help_text = 'This is optional, and isn&rsquo;t shared with anyone'
	)
	
	public = forms.BooleanField(
		label = 'Make my profile public',
		required = False,
		initial = True
	)
	
	def clean_password_confirm(self):
		create_account = self.cleaned_data['create_account'] == 'True'
		password_confirm = self.cleaned_data['password_confirm']
		
		if create_account:
			password = self.cleaned_data['password']
			
			if password != password_confirm:
				raise forms.ValidationError('The two passwords don\'t match.')
			
		return password_confirm
	
	def clean_username(self):
		create_account = self.cleaned_data['create_account'] == 'True'
		username = self.cleaned_data['username']
		
		if create_account:
			if User.objects.filter(username__iexact = username).count() == 1:
				raise forms.ValidationError('Sorry, this username is already in use.')
			
		return username
	
	def clean_email(self):
		create_account = self.cleaned_data['create_account'] == 'True'
		email = self.cleaned_data['email']
		
		if create_account:
			if User.objects.filter(email__iexact = email).count() == 1:
				raise forms.ValidationError('This email address is already in use.')
			
		return email
	
	def clean_email_confirm(self):
		create_account = self.cleaned_data['create_account'] == 'True'
		email_confirm = self.cleaned_data.get('email_confirm')
		
		if create_account:
			email = self.cleaned_data.get('email')
			
			if email != email_confirm:
				raise forms.ValidationError('The two email addresses don\'t match.')

		return email_confirm
	
	def clean(self):
		create_account = self.cleaned_data['create_account'] == 'True'
		if not create_account:
			from django.contrib.auth import authenticate
			
			user = authenticate(
				username = self.cleaned_data['username'],
				password = self.cleaned_data['password']
			)
			
			if not user:
				raise forms.ValidationError('The username and password entered do not match.')
			
			self.user = user
		
		return self.cleaned_data
	
	def save(self, commit = True):
		create_account = self.cleaned_data['create_account'] == 'True'
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']
		
		if create_account:
			user = User.objects.create_user(
				username = username,
				password = password,
				email = self.cleaned_data['email']
			)
			
			from django.contrib.auth import authenticate
			user = authenticate(
				username = username,
				password = password
			)
			
			profile = super(SignupForm, self).save(commit = False)
			profile.user = user
		
			if commit:
				profile.save()
		else:
			profile = self.user.get_profile()
			
		return profile
	
	class Meta:
		model = Profile
		exclude = (
			'user',
		)
		
		fields = (
			'create_account',
			'username',
			'password',
			'password_confirm',
			'email',
			'email_confirm',
			'dob',
			'gender',
			'public'
		)
	
	class Media:
		js = ('js/start-form.js',)