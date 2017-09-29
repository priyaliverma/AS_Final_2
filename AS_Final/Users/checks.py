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

def Tier_1(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		return True
	return False

def Tier_2(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		_Member = Member.objects.get(User=user)
		if _Member.Admin:
			return True		
		elif _Member.Paid:
			return True
	return False

def Tier_3(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		_Member = Member.objects.get(User=user)
		if _Member.Admin:
			return True
		elif _Member.Paid and _Member.Read and _Member.Agreed:
			return True
	return False

def Expired_Check(user):
	_Member = Member.objects.get(User=user)
	if _Member.Admin:
		return True
	if _Member.Expiry_Date < datetime.now(timezone.utc):
		request.session["Expired"] = ["True"]
		return False
	return True
	
# Liability Waiver
def Not_Agreed(user):
	_Member = Member.objects.get(User=user)
	return not _Member.Agreed
# Terms & Conditions
def Not_Read(user):
	_Member = Member.objects.get(User=user)
	return not _Member.Read
# Sign-Up Confirmation
def New_Check(user):
	_Member = Member.objects.get(User=user)
	return _Member.New
# Welcome
def No_Workouts(user):
	_Member = Member.objects.get(User=user)
	return not _Member.Has_Workout



def New_Check_Inverse(user):
	_Member = Member.objects.get(User=user)
	return not _Member.New


def Agreed(user):
	_Member = Member.objects.get(User=user)
	return _Member.Agreed


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

def Agreed_And_Read(user):
	_Member = Member.objects.get(User=user)
	return _Member.Read and _Member.Agreed	

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
