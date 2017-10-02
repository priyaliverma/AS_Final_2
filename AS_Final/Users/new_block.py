# -*- coding: utf-8 -*-
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
from sign_up_views import Get_Weight, Get_Max, Generate_Workouts
from Shared_Functions import User_Check, Member_Exists


def Check_Level_Up(_Member):
	Level_Up = True
	Curr_Level = _Member.Level
	Stats = _Member.Stats.all()
	
	Squat, Created = Stat.objects.get_or_create(Member = _Member, Type="Squat")
	Bench, Created = Stat.objects.get_or_create(Member = _Member, Type="UB Hor Press")
	Hinge, Created = Stat.objects.get_or_create(Member = _Member, Type="Hinge")
	print("CHECK LEVEL UP FUNCTION:")
	for x in Stats:
		print("Stat Check: " + x.Type + " Passed: " + str(not x.Failed))
		if x.Failed and x.Level <= Curr_Level - 2:
			Level_Up = False
	# 	if x.Level < Curr_Level - 2:
	# 		return False
	# 	if x.Failed and x.Core: 
	# 		return False
	if Squat.Failed or Bench.Failed or Hinge.Failed:
		Level_Up = False

	if Level_Up:
		print("Member Levelled Up!")
	# 	_Member.Level += 1
	# 	_Member.save()
		return True
	else:
		return False

@user_passes_test(User_Check, login_url="/")
def Level_Up(request):
	User = request.user
	_Member = Member.objects.get(User=User)
	context = {}
	
	context["Core_Stats"] = []
	context["Stats"] = []
	context["Title"] = "Level Up"
	context["Main_Message"] = "Congratulations, you have levelled up!"
	context["Second_Message"] = "You are now at level: " + str(_Member.Level + 1)
	context["Level"] = _Member.Level

	if not request.session["Level_Up"]:
		context["Main_Message"] = "You need more time!"
		context["Second_Message"] = "You results show that you need to spend more time at your current exercise level. " 						
	
	Stat_List = _Member.Stats.all()
	for i in Stat_List:
		Stat_Dict = {}
		Stat_Dict["Type"] = i.Type
		if i.Failed:
			Stat_Dict["Alloy_Outcome"] = "Failed"
			Stat_Dict["PASSED"] = []
			Stat_Dict["FAILED"] = ["FAILED"]
		else:
			Stat_Dict["Alloy_Outcome"] = "Passed"
			Stat_Dict["PASSED"] = ["PASSED"]
			Stat_Dict["FAILED"] = []
		Stat_Dict["Alloy_Reps"] = i.Alloy_Reps
		Stat_Dict["Alloy_Performance_Reps"] = i.Alloy_Performance_Reps
		Stat_Dict["Exercise_Name"] = i.Exercise_Name
		# Stat_Dict["Exercise_Name"] = i.Exercise_Name
		Stat_Dict["Alloy_Performance_Reps"] = i.Alloy_Performance_Reps
		if i.Type == "Squat" or i.Type == "Hinge" or i.Type == "UB Hor Press":
			context["Core_Stats"].append(Stat_Dict)
		else:
			context["Stats"].append(Stat_Dict)
	# New_Level = str(request.session["New_Level"])
	# context["Level_Up_Message"] = "Congratulations, you've reached Level " + New_Level + " !! You can access the new Level ___ videos"
	return render(request, "levelup.html", context)
