from __future__ import unicode_literals
from .models import *
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.core.files import File
import json
import stripe
from RPE_Dict import RPE_Dict
from level_up_messages import Messages_Dict
import re
from Shared_Functions import *
from checks import *


@user_passes_test(Inside_Access, login_url="/")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
@user_passes_test(Member_Finished_Workouts, login_url="/userpage")
def Get_Workout_Block(request):
	context = {}
	Days_List = []
	Ref_Dict = User_Ref_Dict(request.user)
	context["Level"] = Ref_Dict["Level"]
	context["Num_Days"] = 3

	_Member = Ref_Dict["Member"]
	# _Member.Level = 16
	_Member.Level = 1
	_Member.save()

	N_Days = 3
	Error = False

	if _Member.Level >= 6:
		N_Days = 4
		context["Num_Days"] = 4

	for i in range(N_Days):
		Day_Dict = {}
		Day_Name = "Day " + str(i + 1)
		Day_Code = "Day_" + str(i + 1)
		Day_Dict["Name"] = Day_Name
		Day_Dict["Code"] = Day_Code
		Days_List.append(Day_Dict)

	context["Days_List"] = Days_List

	if request.GET.get("Create_Program"):
		_Member.Has_Workout = True
		_Member.save()
		_Level = _Member.Level
		for Workout in _Member.workouts.all():
			Workout.Completed = True
			Workout.save()
		print("Creating Program")

		Start_Date = datetime.now()

		Days_List = []

		for n in range(N_Days):
			Day_Code = "Day_" + str(n + 1)

			if Day_Code not in request.GET.keys():
				context["Error"] = "Please choose " + str(N_Days) + " different workout days!"
				return render(request, "next_workout_block.html", context)
			Day_Input = request.GET[Day_Code]
			print(Day_Input)
			if Day_Input == "" or Day_Input == "None":
				Error = True
			elif int(Day_Input) in Days_List:
				Error = True
			Days_List.append(int(Day_Input))
			print(Days_List)
		if Error:
			context["Error"] = "Please choose " + str(N_Days) + " different workout days!"
			return render(request, "next_workout_block.html", context)
		if not Error:
			for W in _Member.workouts.all():
				W.Current_Block = False
				W.save()
			_Member.Finished_Workouts = False
			_Member.save()
			Generate_Workouts(Start_Date, _Level, Days_List, _Member)
			return HttpResponseRedirect("/userpage")
	return render(request, "next_workout_block.html", context)

@user_passes_test(Inside_Access, login_url="/")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
@user_passes_test(Member_Finished_Workouts, login_url="/userpage")
def Level_Up(request):
	User = request.user
	_Member = Member.objects.get(User=User)
	# request.session["Level_Up"] = Check_Level_Up(_Member)
	context = {}
	
	context["Core_Stats"] = []
	context["Stats"] = []
	context["Title"] = "Level Up"
	context["Main_Message"] = "Congratulations, you have levelled up!"
	context["Second_Message"] = "You are now at level: " + str(_Member.Level)
	context["Level"] = _Member.Level 
	context["Level_Up"] = ["True"]

	if "Level_Up" not in request.session.keys():
		context["Passed"] = True
		request.session["Level_Up"] = False

	if not request.session["Level_Up"]:
		context["Passed"] = False
		context["Main_Message"] = "You need more time!"
		context["Second_Message"] = "You results show that you need to spend more time at your current exercise level. " 	
	else:					
		context["Level_Up_Message"] = Messages_Dict[16]
		Static_String = str(16) + "_Static"
		context["Level_Up_Img_URL"] = Messages_Dict[Static_String]
		context["Level_Up"] = []
	
	Stat_List = _Member.Stats.all()
	for i in Stat_List:
		Stat_Dict = {}
		Stat_Dict["Type"] = i.Type
		if not i.Level_Up:
			Stat_Dict["Alloy_Outcome"] = "Failed"
			Stat_Dict["PASSED"] = []
			Stat_Dict["FAILED"] = ["FAILED"]
		else:
			Stat_Dict["Alloy_Outcome"] = "Passed"
			Stat_Dict["PASSED"] = ["PASSED"]
			Stat_Dict["FAILED"] = []
		# Stat_Dict["Alloy_Reps"] = i.Alloy_Reps
		# Stat_Dict["Alloy_Performance_Reps"] = i.Alloy_Performance_Reps
		Stat_Dict["Exercise_Name"] = i.Exercise_Name
		# Stat_Dict["Exercise_Name"] = i.Exercise_Name
		# Stat_Dict["Alloy_Performance_Reps"] = i.Alloy_Performance_Reps
		if i.Type == "Squat" or i.Type == "Hinge" or i.Type == "UB Hor Push":
			context["Core_Stats"].append(Stat_Dict)
		else:
			context["Stats"].append(Stat_Dict)
	if request.GET.get("Next_Workouts"):
		return HttpResponseRedirect("/get-workouts")
	# New_Level = str(request.session["New_Level"])
	# context["Level_Up_Message"] = "Congratulations, you've reached Level " + New_Level + " !! You can access the new Level ___ videos"
	return render(request, "levelup.html", context)
