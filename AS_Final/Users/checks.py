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
# SEQUENCE STARTS HERE
def Member_Exists(user):
	if user.is_anonymous():
		return False
		print("Member doens't exist!")
	else:
		return Member.objects.filter(User=user).exists()
def Member_Paid(user):
	_Member = Member.objects.get(User=user)
	if not _Member.Paid:
		print("Member hasn't paid!")		
	return _Member.Paid
# Liability Waiver
def Member_Agreed(user):
	_Member = Member.objects.get(User=user)
	if not _Member.Agreed:
		print("Member hasn't agreed!")		
	return _Member.Agreed
def Not_Agreed(user):
	_Member = Member.objects.get(User=user)
	if _Member.Agreed:
		print("Member already agreed!")		
	return not _Member.Agreed
# Terms & Conditions
def Not_Read(user):
	_Member = Member.objects.get(User=user)
	if _Member.Read:
		print("Member already read!")		
	return not _Member.Read
def Member_Read(user):
	_Member = Member.objects.get(User=user)
	if not _Member.Read:
		print("Member hasn't Read!")		
	return _Member.Read
# Welcome
def Member_Has_Workouts(user):
	_Member = Member.objects.get(User=user)
	if not _Member.Has_Workouts:
		print("Member has no workouts!")		
	return _Member.Has_Workouts
def No_Workouts(user):
	_Member = Member.objects.get(User=user)
	if _Member.Has_Workouts:
		print("Member already has workouts!")		
	return not _Member.Has_Workouts
# Finished Workouts
def Member_Finished_Workouts(user):
	_Member = Member.objects.get(User=user)
	if not _Member.Finished_Workouts:
		print("Member has no workouts!")		
	return _Member.Finished_Workouts

# BELOW TWO USED FOR ALL INSIDE-PAGES (EXCEPT FOR USERPAGE)
# Member Expired
def Member_Not_Expired(user):
	_Member = Member.objects.get(User=user)
	if _Member.Admin:
		return True
	if _Member.Expiry_Date == None or _Member.Expiry_Date < datetime.now(timezone.utc):
		return False
	return True
# INSIDE ACCESS
def Inside_Access(user):
	if user.is_anonymous():
		return False
	else:
		_Member = Member.objects.get(User=user)
		if _Member.Paid and _Member.Agreed and _Member.Read and _Member.Has_Workouts:
			return True
	return False
# FINISHED WORKOUTS
def Member_Finished_Workouts(user):
	_Member = Member.objects.get(User=user)
	return _Member.Finished_Workouts


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

def Read(user):
	_Member = Member.objects.get(User=user)
	return _Member.Read

def Agreed(user):
	_Member = Member.objects.get(User=user)
	return _Member.Agreed

def Tier_3(user):
	if user.is_anonymous():
		return False
	elif Member.objects.filter(User=user).exists():
		_Member = Member.objects.get(User=user)
		if _Member.Admin:
			return True
		elif _Member.Paid and _Member.Read and _Member.Agreed and _Member.Has_Workouts:
			return True
	return False

def Expired_Check(user):
	_Member = Member.objects.get(User=user)
	if _Member.Admin:
		return True
	if _Member.Expiry_Date == None or _Member.Expiry_Date < datetime.now(timezone.utc):
		request.session["Expired"] = ["True"]
		return False
	return True

def Not_New(user):
	_Member = Member.objects.get(User=user)
	return not _Member.New
	
# Sign-Up Confirmation
def New_Check(user):
	_Member = Member.objects.get(User=user)
	return _Member.New


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
