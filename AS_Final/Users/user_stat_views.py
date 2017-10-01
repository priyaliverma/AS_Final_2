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
# from sign_up_views import Get_Weight, Get_Max, Generate_Workouts
from RPE_Dict import *
import re
from checks import *
from Shared_Functions import User_Ref_Dict

Exercise_Types = ["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat", "LB Uni Push", 
"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2", "Carry"]

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

# RPEs = ["X (Failure)", "1-2", "3-4", "5-6", "7", "8", "8.5", "9", "9.5", "10"]

RPEs = [["1-2", 1], ["3-4", 3], ["5-6", 5], ["7", 7], ["8", 8], ["8.5", 8.5], ["9", 9], ["9.5", 9.5], ["10", 10]]
RPEs.reverse()

@user_passes_test(Tier_3, login_url="/")
@user_passes_test(Expired_Check, login_url="/renew-membership")
def User_Profile_View_Workout(request):
	context = {}
	_User = request.user
	Ref_Dict = User_Ref_Dict(_User)
	_PK = request.session["Workout_PK"]
	_Workout = Workout.objects.get(pk=_PK)

	context["Workout_Date"] = _Workout._Date
	context["Workout_Info"] = "Week " + str(_Workout.Template.Week) + ", Day " + str(_Workout.Template.Day)
	context["Workout_Level"] = "Level " + str(_Workout.Level)

	context["Patterns"] = []
	for i in _Workout.SubWorkouts.all():
		Template = i.Template
		print(i.Template.Exercise_Type + " Set Stats: ")
		print(i.Set_Stats)
		Sub_Dict = {}
		Sub_Dict["Number_Sets"] = i.Template.Sets
		Sub_Dict["Sets"] = []
		Sub_Dict["Type"] = i.Template.Exercise_Type
		if i.Exercise != None:
			Sub_Dict["Exercise_Name"] = i.Exercise.Name
		Sets_List = i.Set_Stats.split("/")
		if "" in Sets_List:
			Sets_List.remove("")
		Set_Num = 0
		for Set in Sets_List:
			Set_Num += 1
			print("Set: " + str(Set))
			# if Set != "":
			Set_Dict = {}
			Set_Dict["Set_String"] = Set
			Set_Dict["Code"] = Set[0]
			Set_List = Set.split(",")
			Type_Code = Set_List[0]
			Set_Number = Set_List[0][1]
			if Type_Code == "A" + str(i.Template.Sets):
				Set_Dict["Type"] = "Alloy"
				Type = "(Alloy)"
			else:
				Set_Dict["Type"] = "Regular"
				Type = "(Regular)"
			Reps = Set_List[1]
			Weight = Set_List[2] + " lbs, "
			RPE = Set_List[3]
			Tempo = Set_List[4]

			if Template.Reps == "" or Template.Reps == "0" or Template.Reps == "B":
				Weight = "Bodyweight, "

			Set_Dict["Set_Info"] = "Set " + str(Set_Num) + ": " + Weight + Reps + " reps @ " + RPE + " RPE "
			if Set[0] != "B":
				Sub_Dict["Sets"].append(Set_Dict)
		context["Patterns"].append(Sub_Dict)

	return render(request, "userprofile_view_workout.html", context)

@user_passes_test(Tier_3, login_url="/")
@user_passes_test(Expired_Check, login_url="/renew-membership")
def User_Profile(request):
	context = {}
	_User = request.user
	context["Username"] = _User.username

	context["First_Name"] = _User.first_name
	context["Last_Name"] = _User.last_name
	_Member = Member.objects.get(User=_User)
	context["Expiry_Date"] = _Member.Expiry_Date.date()
	context["Picture_URL"] = "/static/userpage/Profile_Placeholder.png"
	if _Member.Picture != "":
		context["Picture_URL"] = "/" + _Member.Picture.url
	if request.GET.get("Delete_Picture"):

		_Member.Picture = ""
		_Member.save()
		return HttpResponseRedirect("/profile-view")

	if request.POST.get("Edit_Profile"):
		print("Test")
		print request.POST.keys()
		print request.POST["New_First_Name"]
		if "Profile_Pic" in request.FILES.keys():
			print("Got pic")
			print(request.FILES["Profile_Pic"])
			_Pic = File(request.FILES["Profile_Pic"])
			_Member.Picture = _Pic
			_Member.save()
		if request.POST["New_First_Name"] != "":
			_User.first_name = request.POST["New_First_Name"]
			_User.save()
		if request.POST["New_Last_Name"] != "":
			_User.last_name = request.POST["New_Last_Name"]
			_User.save()
			_Member.save()
		if request.POST["Password_Old"] != "":
			Old_Password = request.POST["Password_Old"]
			if _User.check_password(Old_Password):
				Pass_1 = request.POST["Password_1"]
				Pass_2 = request.POST["Password_2"]
				if Pass_1 != "" and Pass_2 != "" and Pass_1 == Pass_2:
					_User.set_password(Pass_1)
					_User.save()
					print("Password Changed")
				else:
					request.session["Password_Error"]
					context["Password_Error"] = "Password Not Changed! Please make sure your input is correct"
		return HttpResponseRedirect("/profile-view")

	if request.POST.get("Extend_Membership"):
		return HttpResponseRedirect("/renew-membership")

	if _User.username == "Test":
		_Member.Admin = True
		_Member.save()
	if _Member.Admin:
		print("You are admin!")
	else:
		print("Regular User")

	_Workouts = _Member.workouts.all()

	context["Completed_Workouts"] = []

	if request.GET.get("Show_Workout_Details"):
		_PK = request.GET["Workout_PK"]
		request.session["Workout_PK"] = _PK
		return HttpResponseRedirect("/profile-view-workout")

	for W in _Workouts:
		_Date = datetime.strptime(W._Date, "%m/%d/%Y")
		# if W.Completed and _Date >= datetime.now() - timedelta(days=30):
		if True:
		# if not W.Completed:
			Dict = {}
			Dict["Date"] = W._Date
			Dict["Week"] = W.Template.Week
			Dict["Day"] = W.Template.Day
			Dict["Level"] = W.Level
			Dict["Level_Group"] = W.Template.Level_Group
			Dict["PK"] = W.pk
			Dict["Block"] = W.Template.Block
			Dict["Level_Block_Info"] = str(W.Level) 
			Dict["Week_Day_Info"] = "Week " + str(W.Template.Week) + ", Day " + str(W.Template.Day)
			# if 
			W.Alloy = False
			for x in W.SubWorkouts.all():
				if x.Template.Alloy:
					W.Alloy = True
					W.save()
			W.Alloy = W.Template.Alloy
			W.save()

			if W.Alloy:
				Dict["Type"] = "Alloy"
			else:
				Dict["Type"] = "Regular"
			context["Completed_Workouts"].append(Dict)

	_Stats = _Member.Stats.all()
	context["Stats"] = []	
	for i in _Stats:
		_Exercise, Created = Exercise.objects.get_or_create(Type=i.Type, Level=_Member.Level)
		# if i.Type == "Squat" or i.Type == "UB Hor Press" or i.Type == "Hinge":
		if True:
			print("Stat: " + i.Type)
			Stat_Dict = {}
			Stat_Dict["Type"] = i.Type
			Stat_Dict["Name"] = _Exercise.Name
			Stat_Dict["Max"] = i.Max
			context["Stats"].append(Stat_Dict)
	print(_Member.Level)
	context["Level"] = _Member.Level
	return render(request, "userprofile_2.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Users(request): 
	context = {}
	context["Users"] = []
	context["Members"] = []
	# _Members = Member.objects.filter(Paid = True, Admin = False)
	_Members = Member.objects.filter(Paid = True)

	for _Member in _Members:
		_User = _Member.User
		Member_Dict = {}
		Member_Dict["Username"] = _User.username
		Member_Dict["PK"] = _Member.pk
		Member_Dict["First_Name"] = _User.first_name
		Member_Dict["Last_Name"] = _User.last_name
		context["Members"].append(Member_Dict)

	if request.method == 'GET':
		print("GET REQUEST RECEIVED")
	if request.method == 'POST':
		print("POST REQUEST RECEIVED")
		keys = []
		for i in request.POST.keys():
			keys.append(i)
			print(i)
			print(type(i))
			print(len(i))
			if len(i) < 4:
				request.session["Member_PK"] = str(i)
				# request.session["User_PK"] = str(i)
		print("POST REQUEST RECEIVED")
		return HttpResponseRedirect("/admin-users-view-profile/")
	return render(request, "admin_users.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_User_Profile (request):

	Member_PK = int(request.session["Member_PK"])
	_Member = Member.objects.get(pk=Member_PK)
	_User = _Member.User
	_Workouts = _Member.workouts.all()
	_Now = datetime.now()
	_Past_Times = []
	_Future_Times = []

	context = {}

	context["Picture_URL"] = "/static/userpage/Profile_Placeholder.png"
	if _Member.Picture != "":
		context["Picture_URL"] = "/" + _Member.Picture.url

	context["User_Info"] = {}
	context["User_Info"]["Username"] = _User.username
	context["User_Info"]["First_Name"] = _User.first_name
	context["User_Info"]["Last_Name"] = _User.last_name
	context["User_Info"]["Level"] = _Member.Level
	context["User_Info"]["Stats"] = []
	# User Info
	context["DOB"] = _Member.DOB
	context["Height"] = _Member.Height
	context["Weight"] = _Member.Weight
	# Training Experience
	context["Training_Time"] = _Member.Training_Time
	context["Sports"] = _Member.Primary_Sports
	if _Member.Prior_RPE:
		context["RPE"] = "Yes"
	else:
		context["RPE"] = "No"
	# Lifts from Sign-Up
	if _Member.Squat == 0:
		context["Squat"] = "None"
	else:
		context["Squat"] = _Member.Squat

	if _Member.Bench == 0:
		context["Bench"] = "None"
	else:
		context["Bench"] = _Member.Bench

	if _Member.D_Lift == 0:
		context["D_Lift"] = "None"
	else:
		context["D_Lift"] = _Member.D_Lift

	if _Member.OP == 0:
		context["OP"] = "None"
	else:
		context["OP"] = _Member.OP

	if _Member.PC == 0:
		context["PC"] = "None"
	else:
		context["PC"] = _Member.PC

	if _Member.CJerk == 0:
		context["CJerk"] = "None"
	else:
		context["CJerk"] = _Member.CJerk

	if _Member.Snatch == 0:
		context["Snatch"] = "None"
	else:
		context["Snatch"] = _Member.Snatch

	if _Member.Other == "":
		context["Other"] = "None"
	else:
		context["Other"] = _Member.Other

	_Stats = _Member.Stats.all()
	for i in _Stats:
		_Exercise, Created = Exercise.objects.get_or_create(Type=i.Type, Level=_Member.Level)
		# if i.Type == "Squat" or i.Type == "UB Hor Press" or i.Type == "Hinge":
		if True:
			print("Stat: " + i.Type)
			Stat_Dict = {}
			Stat_Dict["Type"] = i.Type
			Stat_Dict["Name"] = _Exercise.Name
			Stat_Dict["Max"] = i.Max
			context["User_Info"]["Stats"].append(Stat_Dict)


	for i in _Workouts:
		_Datetime = datetime.strptime(i._Date, '%m/%d/%Y')
		i.Date = _Datetime.date()
		i.save()
		# print(str(i) + " " + i._Date + " " + str(datetime.strptime(i._Date, '%m/%d/%Y')))
		if _Datetime >_Now:
			_Distance = _Datetime - datetime.now()
			_Future_Times.append(_Distance)
			if _Distance <= min(_Future_Times):
				Next_Workout = i
		elif _Datetime < _Now:
			_Distance = datetime.now() - _Datetime
			_Past_Times.append(_Distance)
			if _Distance <= min(_Past_Times):
				Last_Workout = i

	context["Next_Workout"] = {}
	context["Last_Workout"] = {}

	if _Future_Times:
		_Summary = "Level " + str(Next_Workout.Level) + ", Week " + str(Next_Workout.Template.Week) + " Day " + str(Next_Workout.Template.Day)
		if Next_Workout.Template.Alloy:
			_Summary += " (Alloy)"
		context["Next_Workout"]["Summary"] = _Summary
		context["Next_Workout"]["Date"] = Next_Workout._Date
		context["Next_Workout"]["PK"] = Next_Workout.pk
		context["Next_Workout"]["Subs"] = []
		for i in Next_Workout.SubWorkouts.all():
			Template = i.Template
			Sub_Dict = {}
			Sub_Dict["Number_Sets"] = i.Template.Sets
			Sub_Dict["Sets"] = []
			Sub_Dict["Type"] = i.Template.Exercise_Type
			if i.Exercise != None:
				Sub_Dict["Exercise_Name"] = i.Exercise.Name
			Sets_List = i.Set_Stats.split("/")
			if "" in Sets_List:
				Sets_List.remove("")
			Set_Num = 0
			for Set in Sets_List:
				Set_Num += 1
				Set_Dict = {}
				Set_Dict["Set_String"] = Set
				Set_Dict["Code"] = Set[0]
				Set_List = Set.split(",")
				Type_Code = Set_List[0]
				Set_Number = Set_List[0][1]
				if Type_Code == "A" + str(i.Template.Sets):
					Set_Dict["Type"] = "Alloy"
					Type = "(Alloy)"
				else:
					Set_Dict["Type"] = "Regular"
					Type = "(Regular)"
				Reps = Set_List[1]
				Weight = Set_List[2] + " lbs, "
				RPE = Set_List[3]
				Tempo = Set_List[4]
				if Template.Reps == "" or Template.Reps == "0" or Template.Reps == "B":
					Weight = "Bodyweight, "
				Set_Dict["Set_Info"] = "Set " + str(Set_Num) + ": " + Weight + Reps + " reps @ " + RPE + " RPE "
				if Set[0] != "B":
					Sub_Dict["Sets"].append(Set_Dict)
			context["Next_Workout"]["Subs"].append(Sub_Dict)
		# _Subs = []
	else:
		context["Next_Workout"]["None"] = True

	if request.GET.get("View_Next_Workout"):
		request.session["Workout_PK"] = int(request.GET["Next_Workout_PK"])
		return HttpResponseRedirect("/admin-users-view-profile-workout")

	if _Past_Times:
		_Summary = "Level " + str(Last_Workout.Level) + ", Week " + str(Last_Workout.Template.Week) + " Day " + str(Last_Workout.Template.Day)
		if Last_Workout.Template.Alloy:
			_Summary += " (Alloy)"
		context["Last_Workout"]["Summary"] = _Summary
		context["Last_Workout"]["Date"] = Last_Workout._Date
		context["Last_Workout"]["PK"] = Last_Workout.pk
		context["Last_Workout"]["Subs"] = []
		for i in Last_Workout.SubWorkouts.all():
			Template = i.Template
			Sub_Dict = {}
			Sub_Dict["Number_Sets"] = i.Template.Sets
			Sub_Dict["Sets"] = []
			Sub_Dict["Type"] = i.Template.Exercise_Type
			if i.Exercise != None:
				Sub_Dict["Exercise_Name"] = i.Exercise.Name
			Sets_List = i.Set_Stats.split("/")
			if "" in Sets_List:
				Sets_List.remove("")
			Set_Num = 0
			for Set in Sets_List:
				Set_Num += 1
				Set_Dict = {}
				Set_Dict["Set_String"] = Set
				Set_Dict["Code"] = Set[0]
				Set_List = Set.split(",")
				Type_Code = Set_List[0]
				Set_Number = Set_List[0][1]
				if Type_Code == "A" + str(i.Template.Sets):
					Set_Dict["Type"] = "Alloy"
					Type = "(Alloy)"
				else:
					Set_Dict["Type"] = "Regular"
					Type = "(Regular)"
				Reps = Set_List[1]
				Weight = Set_List[2] + " lbs, "
				RPE = Set_List[3]
				Tempo = Set_List[4]
				if Template.Reps == "" or Template.Reps == "0" or Template.Reps == "B":
					Weight = "Bodyweight, "
				Set_Dict["Set_Info"] = "Set " + str(Set_Num) + ": " + Weight + Reps + " reps @ " + RPE + " RPE "
				if Set[0] != "B":
					Sub_Dict["Sets"].append(Set_Dict)
			context["Last_Workout"]["Subs"].append(Sub_Dict)
	else:
		context["Last_Workout"]["None"] = True		

	if request.GET.get("View_Last_Workout"):
		request.session["Workout_PK"] = int(request.GET["Last_Workout_PK"])
		return HttpResponseRedirect("/admin-users-view-profile-workout")


	return render(request, "admin_user_profile.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_User_Workout (request):
	context = {}

	Member_PK = int(request.session["Member_PK"])
	_Member = Member.objects.get(pk=Member_PK)
	_User = _Member.User
	context["Member_Name"] = _User.first_name + " " + _User.last_name

	_PK = request.session["Workout_PK"]
	_Workout = Workout.objects.get(pk=_PK)

	context["Workout_Date"] = _Workout._Date
	context["Workout_Info"] = "Week " + str(_Workout.Template.Week) + ", Day " + str(_Workout.Template.Day)
	context["Workout_Level"] = "Level " + str(_Workout.Level)

	context["Patterns"] = []
	for i in _Workout.SubWorkouts.all():
		Template = i.Template
		print(i.Template.Exercise_Type + " Set Stats: ")
		print(i.Set_Stats)
		Sub_Dict = {}
		Sub_Dict["Number_Sets"] = i.Template.Sets
		Sub_Dict["Sets"] = []
		Sub_Dict["Type"] = i.Template.Exercise_Type
		if i.Exercise != None:
			Sub_Dict["Exercise_Name"] = i.Exercise.Name
		Sets_List = i.Set_Stats.split("/")
		if "" in Sets_List:
			Sets_List.remove("")
		Set_Num = 0
		for Set in Sets_List:
			Set_Num += 1
			print("Set: " + str(Set))
			# if Set != "":
			Set_Dict = {}
			Set_Dict["Set_String"] = Set
			Set_Dict["Code"] = Set[0]
			Set_List = Set.split(",")
			Type_Code = Set_List[0]
			Set_Number = Set_List[0][1]
			if Type_Code == "A" + str(i.Template.Sets):
				Set_Dict["Type"] = "Alloy"
				Type = "(Alloy)"
			else:
				Set_Dict["Type"] = "Regular"
				Type = "(Regular)"
			Reps = Set_List[1]
			Weight = Set_List[2] + " lbs, "
			RPE = Set_List[3]
			Tempo = Set_List[4]

			if Template.Reps == "" or Template.Reps == "0" or Template.Reps == "B":
				Weight = "Bodyweight, "

			Set_Dict["Set_Info"] = "Set " + str(Set_Num) + ": " + Weight + Reps + " reps @ " + RPE + " RPE "
			if Set[0] != "B":
				Sub_Dict["Sets"].append(Set_Dict)
		context["Patterns"].append(Sub_Dict)

	return render(request, "admin_user_workout_summary.html", context)



@user_passes_test(Tier_3, login_url="/")
@user_passes_test(Expired_Check, login_url="/renew-membership")
def User_Stats(request):
	context = {}
	_User = request.user
	_Member = Member.objects.get(User=_User)
	print(_Member.Level)

	if request.GET.get("Show_Workout_Details"):
		_PK = request.GET["Workout_PK"]
		request.session["Workout_PK"] = _PK
		return HttpResponseRedirect("/profile-view-workout")

	_Stats = _Member.Stats.all()
	context["Stats"] = []	
	for i in _Stats:
		_Exercise = Exercise.objects.get_or_create(Type=i.Type, Level=_Member.Level)
		print("Stat: " + i.Type)
		context["Stats"].append([i.Type, i.Type, i.Max])

	_Workouts = _Member.workouts.all()

	context["Completed_Workouts"] = []
	for W in _Workouts:
		_Date = datetime.strptime(W._Date, "%m/%d/%Y")

		# if W.Completed and _Date >= datetime.now() - timedelta(days=30):
		if True:
			Dict = {}
			Dict["Date"] = W._Date
			Dict["Week"] = W.Template.Week
			Dict["Day"] = W.Template.Day
			Dict["Level"] = W.Level
			Dict["Level_Group"] = W.Template.Level_Group
			Dict["PK"] = W.pk
			Dict["Block"] = W.Template.Block
			Dict["Level_Block_Info"] = "Level " + str(W.Level) + " " + W.Template.Block
			Dict["Week_Day_Info"] = "Week " + str(W.Template.Week) + ", Day " + str(W.Template.Day)
			# if 
			W.Alloy = False
			for x in W.SubWorkouts.all():
				if x.Template.Alloy:
					W.Alloy = True
					W.save()
			W.Alloy = W.Template.Alloy
			W.save()

			if W.Alloy:
				if W.Alloy_Passed:
					Dict["Type"] = "Alloy (Passed)"
				else:
					Dict["Type"] = "Alloy (Failed)"
			else:
				Dict["Type"] = "Regular"
			context["Completed_Workouts"].append(Dict)
	# 	Related_Exercise = Exercise.objects.get(Level = _Member.Level, Type = i.Type)
	# 	i.Exercise_Name = Related_Exercise.Name
	# 	i.save()
	# 	if i.Type == "":
	# 		i.delete()
	if request.GET.get("Reset_All"):
		print("Resetting All")
		for Workout in _Member.workouts.all():
			for Sub in Workout.SubWorkouts.all():
				Sub.delete()
			Workout.delete()
		for Stat in _Member.Stats.all():
			Stat.delete()
		return HttpResponseRedirect("/profile-stats")
	return render(request, "userstats.html", context)
