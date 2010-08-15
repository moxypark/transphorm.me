#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.contrib.auth.models import User
from transphorm.goals.models import Profile, Plan, Goal, Action, Reward, \
	Milestone, LogEntry, ActionEntry, RewardClaim, Comment
from transphorm.goals.widgets import RadioSelectWithHelpText

class ProfileForm(forms.ModelForm):
	first_name = forms.RegexField(
		regex = r"^[a-zA-Z']+$"
	)
	
	last_name = forms.RegexField(
		regex = r"^[a-zA-Z-']+$"
	)
	
	username = forms.RegexField(
		regex = r'^[a-z0-9]+$'
	)
	
	password = forms.CharField(
		widget = forms.PasswordInput,
		required = False,
		label = 'Change your password'
	)
	
	password_confirm = forms.CharField(
		label = 'Confirm your password',
		widget = forms.PasswordInput,
		required = False
	)
	
	email = forms.EmailField(
		label = 'Email address'
	)
	
	twitter = forms.RegexField(
		regex = r'^[a-z0-9_]+$',
		required = False
	)
	
	def clean_password_confirm(self):
		password = self.cleaned_data.get('password', None)
		password_confirm = self.cleaned_data['password_confirm']
		
		if password and password != password_confirm:
			raise forms.ValidationError('The two passwords don\'t match.')
			
		return password_confirm
	
	def clean_username(self):
		username = self.cleaned_data.get('username', None)
		user_id = self.instance.user.pk
		
		if User.objects.filter(
			username__iexact = username
		).exclude(
			pk = user_id
		).count() == 1:
			raise forms.ValidationError(
				'Sorry, this username is already in use.'
			)
		
		return username
	
	def clean_email(self):
		email = self.cleaned_data['email']
		user_id = self.instance.user.pk
		
		if email:
			if User.objects.filter(
				email__iexact = email
			).exclude(
				pk = user_id
			).count() == 1:
				raise forms.ValidationError(
					'This email address is already in use.'
				)
		else:
			raise forms.ValidationError('This field is required.')
			
		return email
	
	def __init__(self, *args, **kwargs):
		from datetime import date
		this_year = date.today().year
		
		years = range(this_year - 100, this_year - 12)
		years.reverse()
		
		super(ProfileForm, self).__init__(*args, **kwargs)
		self.fields['about'].label = 'Tell us about yourself'
		self.fields['public'].label = 'Make my profile public'
		self.fields['dob'].widget = SelectDateWidget(
			years = years
		)
		
		self.fields['first_name'].initial = self.instance.user.first_name
		self.fields['last_name'].initial = self.instance.user.last_name
		self.fields['username'].initial = self.instance.user.username
		self.fields['email'].initial = self.instance.user.email
	
	def save(self, commit = True):
		profile = super(ProfileForm, self).save(commit = False)
		
		profile.user.username = self.cleaned_data.get('username', None)
		profile.user.first_name = self.cleaned_data['first_name']
		profile.user.last_name = self.cleaned_data['last_name']
		
		if not self.cleaned_data['password'] is None and not \
			self.cleaned_data['password'] == '':
			profile.user.set_password(
				self.cleaned_data['password']
			)
		
		profile.user.email = self.cleaned_data['email']
		
		if commit:
			profile.user.save()
			profile.save()
	
	class Meta:
		model = Profile
		exclude = ('user',)
		fields = (
			'first_name',
			'last_name',
			'username',
			'password',
			'password_confirm',
			'email',
			'public',
			'dob',
			'gender',
			'about',
			'twitter',
			'website',
		)

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
		self.fields['deadline'].widget = SelectDateWidget(
			attrs = {
				'class': 'date-field future-date'
			}
		)
		
		if not self.instance.original:
			del self.fields['live']
			del self.fields['allow_copies']
		
		if not self.instance.goal.has_deadline:
			self.fields['deadline'].required = False
			self.fields['deadline'].help_text = """You don&rsquo;t have to
			set a deadline for this goal, but it can be helpful"""
	
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
		help_text = """It should be in lowercase. Imagine it in a sentence,
		starting with &ldquo;I want to...&rdquo;"""
	)
	
	description = forms.CharField(
		label = 'Tell us a bit about your goal', widget = forms.Textarea,
		help_text = """Why is it an important goal for you and others to
		try and achieve?""",
	)
	
	has_deadline = forms.BooleanField(
		label = 'Can people set a deadline for this goal?',
		required = False
	)
	
	def clean_name(self):
		name = self.cleaned_data['name']
		if name[0].isupper():
			raise forms.ValidationError(
				'Please don\'t start with a capital letter.'
			)
		
		if name.lower().startswith('i want to'):
			raise forms.ValidationError(
				"Please don\'t start with the phrase 'I want to'."
			)
		
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
		regex = r'^[a-z0-9]+$'
	)
	
	password = forms.CharField(
		widget = forms.PasswordInput
	)
	
	password_confirm = forms.CharField(
		label = 'Confirm your password',
		widget = forms.PasswordInput,
		required = False
	)
	
	email = forms.EmailField(
		label = 'Email address',
		required = False
	)
	
	email_confirm = forms.EmailField(
		label = 'Confirm your eemail address',
		required = False
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
	
	def __init__(self, *args, **kwargs):
		from datetime import date
		this_year = date.today().year
		
		years = range(this_year - 100, this_year - 12)
		years.reverse()
		
		super(SignupForm, self).__init__(*args, **kwargs)
		self.fields['dob'].widget = SelectDateWidget(
			years = years, attrs = {
				'class': 'date-field past-date'
			}
		)
		self.fields['dob'].label = 'Date of birth'
		self.fields['dob'].required = False
		self.fields['dob'].help_text = """This is optional, and
		isn&rsquo;t shared with anyone"""
	
	def clean_password_confirm(self):
		create_account = self.cleaned_data.get('create_account') == 'True'
		password_confirm = self.cleaned_data['password_confirm']
		
		if create_account:
			password = self.cleaned_data.get('password', None)
			
			if password != password_confirm:
				raise forms.ValidationError(
					'The two passwords don\'t match.'
				)
			
		return password_confirm
	
	def clean_username(self):
		create_account = self.cleaned_data.get('create_account') == 'True'
		username = self.cleaned_data.get('username', None)
		
		if create_account:
			if User.objects.filter(username__iexact = username).count() == 1:
				raise forms.ValidationError(
					'Sorry, this username is already in use.'
				)
			
		return username
	
	def clean_email(self):
		create_account = self.cleaned_data.get('create_account') == 'True'
		email = self.cleaned_data['email']
		
		if create_account:
			if email:
				if User.objects.filter(email__iexact = email).count() == 1:
					raise forms.ValidationError(
						'This email address is already in use.'
					)
			else:
				raise forms.ValidationError('This field is required.')
			
		return email
	
	def clean_email_confirm(self):
		create_account = self.cleaned_data.get('create_account') == 'True'
		email_confirm = self.cleaned_data.get('email_confirm')
		
		if create_account:
			email = self.cleaned_data.get('email')
			
			if email != email_confirm:
				raise forms.ValidationError(
					'The two email addresses don\'t match.'
				)
		
		return email_confirm
	
	def clean(self):
		create_account = self.cleaned_data.get('create_account') == 'True'
		if not create_account:
			from django.contrib.auth import authenticate
			
			user = authenticate(
				username = self.cleaned_data.get('username'),
				password = self.cleaned_data.get('password')
			)
			
			if not user:
				raise forms.ValidationError(
					"""Please enter a correct username and password.
					Note that both fields are case-sensitive."""
				)
			
			self.user = user
		
		return self.cleaned_data
	
	def save(self, commit = True):
		create_account = self.cleaned_data.get('create_account') == 'True'
		username = self.cleaned_data.get('username', None)
		password = self.cleaned_data.get('password', None)
		
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
			try:
				profile = self.user.get_profile()
			except Profile.DoesNotExist:
				profile = Profile(user = self.user)
			
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

class ActionForm(forms.ModelForm):
	ACTION_HELP = (
		"""Something simple, that adds or deducts a fixed number of
		points to or from your total (eg: walked to work).""",
		"""The more you do something, the more points you get
		(eg: walked <em>x</em> miles today).""",
	)
	
	def __init__(self, *args, **kwargs):
		super(ActionForm, self).__init__(*args, **kwargs)
		
		self.fields['kind'].widget = RadioSelectWithHelpText(
			choices = self.fields['kind'].choices[1:],
			choice_help_text = self.ACTION_HELP
		)
		
		self.fields['measurement'].required = False
	
	class Meta:
		model = Action
		exclude = (
			'plan'
		)
	
	class Media:
		js = ('js/action-form.js',)

class BaseActionFormSet(BaseModelFormSet):
	def __init__(self, *args, **kwargs):
		self.plan = kwargs.pop('plan', None)
		kwargs['queryset'] = self.plan.actions.all()
		super(BaseActionFormSet, self).__init__(*args, **kwargs)
	
	def _construct_form(self, i, **kwargs):
		form = super(BaseActionFormSet, self)._construct_form(i, **kwargs)
		if form.instance:
			form.instance.plan = self.plan

		return form

ActionFormSet = modelformset_factory(
	Action, form = ActionForm, formset = BaseActionFormSet,
	can_delete = True
)

class RewardForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(RewardForm, self).__init__(*args, **kwargs)
	
	class Meta:
		model = Reward
		exclude = (
			'plan'
		)
	
	class Media:
		js = ('js/reward-form.js',)

class BaseRewardFormSet(BaseModelFormSet):
	def __init__(self, *args, **kwargs):
		self.plan = kwargs.pop('plan', None)
		kwargs['queryset'] = self.plan.rewards.all()
		super(BaseRewardFormSet, self).__init__(*args, **kwargs)
	
	def _construct_form(self, i, **kwargs):
		form = super(BaseRewardFormSet, self)._construct_form(i, **kwargs)
		if form.instance:
			form.instance.plan = self.plan
		
		return form

RewardFormSet = modelformset_factory(
	Reward, form = RewardForm, formset = BaseRewardFormSet,
	can_delete = True
)

class MilestoneForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(MilestoneForm, self).__init__(*args, **kwargs)
		self.fields['deadline'].widget = SelectDateWidget(
			attrs = {
				'class': 'date-field future-date'
			}
		)
	
	class Meta:
		model = Milestone
		exclude = (
			'plan',
			'reached'
		)
	
	class Media:
		js = ('js/milestone-form.js',)

class BaseMilestoneFormSet(BaseModelFormSet):
	def __init__(self, *args, **kwargs):
		self.plan = kwargs.pop('plan', None)
		kwargs['queryset'] = self.plan.milestones.all()
		super(BaseMilestoneFormSet, self).__init__(*args, **kwargs)
	
	def _construct_form(self, i, **kwargs):
		form = super(BaseMilestoneFormSet, self)._construct_form(i, **kwargs)
		if form.instance:
			form.instance.plan = self.plan
		
		return form

MilestoneFormSet = modelformset_factory(
	Milestone, form = MilestoneForm, formset = BaseMilestoneFormSet,
	can_delete = True
)

class LogEntryForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(LogEntryForm, self).__init__(*args, **kwargs)
		if 'body' in self.fields:
			self.fields['body'].label = 'How are you doing?'
	
	class Meta:
		model = LogEntry
		
		exclude = (
			'plan'
		)
		
		fields = (
			'body',
		)
	
	class Media:
		js = ('js/log-entry-form.js',)

class CommentForm(LogEntryForm):
	def __init__(self, *args, **kwargs):
		super(CommentForm, self).__init__(*args, **kwargs)
		self.fields['body'].label = 'What would you like to say?'
	
	class Meta:
		model = Comment
		exclude = (
			'plan',
			'kind',
			'date',
			'is_spam',
			'is_approved'
		)
	
	class Media:
		js = ('js/comment-form.js',)

class RewardClaimForm(LogEntryForm):
	def __init__(self, *args, **kwargs):
		super(RewardClaimForm, self).__init__(*args, **kwargs)
		self.fields['reward'].label = 'What reward would you like to claim?'
	
	class Meta:
		model = RewardClaim
		exclude = (
			'plan',
			'kind',
			'body'
		)

class ActionEntryForm(LogEntryForm):
	def __init__(self, *args, **kwargs):
		super(ActionEntryForm, self).__init__(*args, **kwargs)
		self.fields['action'].label = 'What have you done today?'
		self.fields['value'].required = False
		
		self.fields['date'].widget = SelectDateWidget(
			attrs = {
				'class': 'date-field past-dates'
			}
		)
	
	def save(self, commit = True):
		entry = super(ActionEntryForm, self).save(commit = False)
		
		# A bit of a hack. We don't want users to have to bother with
		# entering the timem for their log entries, but we want them to
		# display in the order we created them. If the below isn't done,
		# they'll display in a seemingly random order.
		
		from datetime import date, datetime
		if self.cleaned_data['date'].date() == date.today():
			entry.date = datetime.now()
		
		if commit:
			entry.save()
		
		return entry
	
	class Meta:
		model = ActionEntry
		exclude = (
			'plan',
			'kind',
			'body'
		)
		
		fields = (
			'action',
			'value',
			'date'
		)