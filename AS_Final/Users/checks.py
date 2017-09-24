from __future__ import unicode_literals
from .models import *
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
from django.contrib.auth import logout, login, authenticate
from django.core.files import File
from django.utils import timezone
import json
import stripe     
import re

def User_Check(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		_Member = Member.objects.get(User=user)
		if _Member.Admin:
			return True
		elif _Member.Paid and _Member.Expiry_Date >= datetime.now(timezone.utc):
			return True
		else:
			return False
	else:
		return False

def Admin_Check(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		_Member = Member.objects.get(User=user)
		if _Member.Admin:
			return True
	return False

def Member_Exists(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		return True
	return False

def Member_Paid(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		_Member = Member.objects.get(User=user)
		if _Member.Paid and _Member.Expiry_Date >= datetime.now(timezone.utc):
			return True
	return False
