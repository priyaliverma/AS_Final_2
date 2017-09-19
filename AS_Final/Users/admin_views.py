# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
from django.contrib.auth import logout, login, authenticate
from django.core.files import File
import json
import stripe
from .views import Levels, Exercise_Types
from Shared_Functions import Admin_Check

def Admin_Logout(request):
	logout(request)
	return HttpResponseRedirect("/admin-login")

def Admin_Login(request):
	context = {}
	context["Login_Failed"] = ""
	Logged_In = False
	if request.POST.get("Login"):
		_Username = request.POST["Username"]
		_Password = request.POST["Password"]
		user = authenticate(username=_Username, password=_Password)
		if user is not None:
			if Member.objects.filter(User=user).exists():
				_Member = Member.objects.get(User=user)
				if _Member.Admin:
					print("User authenticated")
			    	login(request, user)
			    	Logged_In = True
				# else:
				# 	context["Login_Failed"] = "Login Failed!"
		if Logged_In:
			return HttpResponseRedirect('/admin-users')
		else:
			context["Login_Failed"] = "Login Failed!"
			return render(request, "admin_login.html", context)
	return render(request, "admin_login.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Users(request): 
	context = {}
	context["Users"] = []
	for _User in User.objects.all():
		if Member.objects.filter(User=_User).exists():
			_Member = Member.objects.get(User=_User)
			row = []
			row.append(_User.username)
			row.append(_User.pk)
			row.append(_User.first_name)
			row.append(_User.last_name)
			context["Users"].append(row)
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
				request.session["User_PK"] = str(i)
		print("POST REQUEST RECEIVED")
		return HttpResponseRedirect("/admin-users-view-profile/")
	return render(request, "admin_users.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_User_Profile (request):
	User_PK = int(request.session["User_PK"])
	_User = User.objects.get(pk=User_PK)
	_Member = Member.objects.get(User=_User)
	_Workouts = _Member.workouts.all()
	_Now = datetime.now()
	_Past_Times = []
	_Future_Times = []
	print("From Admin User Profile: " + str(User_PK))
	print("Current Time: " + str(datetime.now()))
	context = {}
	context["User_Info"] = []
	context["User_Info"].append(_User.username)
	context["User_Info"].append(_User.first_name)
	context["User_Info"].append(_User.last_name)
	context["User_Info"].append(_Member.Level)
	for i in _Workouts:
		_Datetime = datetime.strptime(i._Date, '%m/%d/%Y')
		i.Date = _Datetime.date()
		i.save()
		# print(str(i) + " " + i._Date + " " + str(datetime.strptime(i._Date, '%m/%d/%Y')))
		print(str(i) + " " + i._Date + " " + str(i.Date))
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
	print(_Future_Times)
	print(_Past_Times)
	context["Next_Workout"] = []
	context["Last_Workout"] = []
	if _Future_Times:
		print("Future Min Time: " + str(min(_Future_Times)))
		print("Next Workout: " + str(Next_Workout) + " " + Next_Workout._Date)
		_Summary = ", Level " + str(Next_Workout.Level) + " Week " + str(Next_Workout.Week) + " Day " + str(Next_Workout.Day)
		context["Next_Workout"].append(_Summary)
		context["Next_Workout"].append(Next_Workout._Date)
		_Subs = []
		for _sub in Next_Workout.SubWorkouts.all():
			_Description = str(_sub.Sets) + " x " + str(_sub.Reps) + " " + _sub.Exercise.Name
			_Subs.append(_Description)
		context["Next_Workout"].append(_Subs)
	else:
		context["Next_Workout"].append("None")		
	if _Past_Times:
		print("Past Min Time: " + str(min(_Past_Times)))
		print("Last Workout: " + str(Last_Workout) + " " + Last_Workout._Date)	
		_Summary = ", Level " + str(Last_Workout.Level) + " Week " + str(Last_Workout.Template.Week) + " Day " + str(Last_Workout.Template.Day)
		context["Last_Workout"].append(_Summary)
		context["Last_Workout"].append(Last_Workout._Date)
		_Subs = []
		for _sub in Last_Workout.SubWorkouts.all():
			_Description = str(_sub.Sets) + " x " + str(_sub.Reps) + " " + _sub.Exercise.Name
			_Subs.append(_Description)
		context["Last_Workout"].append(_Subs)
	else:
		context["Last_Workout"].append("None")

	return render(request, "admin_user_profile.html", context)


Level_Group_1_Exercises = [["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat"], 
["LB Uni Push", "Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4"]]

@user_passes_test(Admin_Check, login_url="/admin-login")
def AdminExercises(request):
	context = {}

	LG_1_Exercises = [
	[["UB Hor Push", ["", "", "", "", ""], "HPush"],
	["Hinge", ["", "", "", "", ""], "H"], ["Squat", ["", "", "", "", ""], "S"], 
	["UB Vert Push", ["", "", "", "", ""], "VPush"],  
	["UB Hor Pull", ["", "", "", "", ""], "HPull"], 
	["UB Vert Pull", ["", "", "", "", ""], "VPull"]],

	[["LB Uni Push", ["", "", "", "", ""], "UniPush"], ["Ant Chain", ["", "", "", "", ""], "AC"], 
	["Post Chain", ["", "", "", "", ""], "PC"], ["Isolation", ["", "", "", "", ""], "I1"], 
	["Iso 2", ["", "", "", "", ""], "I2"], ["Iso 3", ["", "", "", "", ""], "I3"], 
	["Iso 4", ["", "", "", "", ""], "I4"]],

	[
	# ["Metabolic Cond", ["", "", "", "", ""], "MC"], 
	# ["Work Capacity", ["", "", "", "", ""], "WC"], 
	["RFD Load", ["", "", "", "", ""], "RL"], ["RFD Unload 1", ["", "", "", "", ""], "RU1"], 
	["RFD Unload 2", ["", "", "", "", ""], "RU2"], 
	["Medicine Ball", ["", "", "", "", ""], "MB"]
	]
	]

	Level_Groups = [
	[["Level 1", "L1", [], [], []], ["Level 2", "L2", [], [], []], ["Level 3", "L3", [], [], []], ["Level 4", "L4", [], [], []], ["Level 5", "L5", [], [], []]],
	[["Level 6", "L6", [], [], []], ["Level 7", "L7", [], [], []], ["Level 8", "L8", [], [], []], ["Level 9", "L9", [], [], []], ["Level 10", "L10", [], [], []]],
	[["Level 11", "L11", [], [], []], ["Level 12", "L12", [], [], []], ["Level 13", "L13", [], [], []], ["Level 14", "L14", [], [], []], ["Level 15", "L15", [], [], []]],
	[["Level 16", "L16", [], [], []], ["Level 17", "L17", [], [], []], ["Level 18", "L18", [], [], []], ["Level 19", "L19", [], [], []], ["Level 20", "L20", [], [], []]],
	[["Level 21", "L21", [], [], []], ["Level 22", "L22", [], [], []], ["Level 23", "L23", [], [], []], ["Level 24", "L24", [], [], []], ["Level 25", "L25", [], [], []]]]

	# for i in Level_Groups:
	# 		for x in i:
	# 			if Level_Groups.index(i) != 0:
	# 				x = x + [[], [], []]
	# 			print(x)
	# print(Level_Groups[1])
	context["Level_Groups"] = [["1-5", 1], ["6-10", 2], ["11-15", 3], ["16-20", 4], ["21-25", 5]]
	# print("Context Levels: " + str(context["Levels"][0]))

	All_Exercises = Exercise.objects.all()
	for _Exercise in All_Exercises:
		if "Tempo" in _Exercise.Name:
			print(_Exercise.Name + " Level: " + str(_Exercise.Level))
			_Exercise.Tempo = True
			_Exercise.save()
	# All_Templates = Workout_Template.objects.all()
	# for _Temp

	if request.method == "POST":
		# print("Post Detected")
		# print(request.POST["level_group"])
		L_Group = int(request.POST["level_group"])
		request.session["Level_Group"] = L_Group

	if "Level_Group" not in request.session.keys():
		request.session["Level_Group"] = 1

	print("Level Group: " + str(request.session["Level_Group"]))

	Selected_L_Group_Index = request.session["Level_Group"] - 1
	Level_Constant = Selected_L_Group_Index*5

	context["Selected_Group"] = [context["Level_Groups"][Selected_L_Group_Index]]
	context["Level_Groups"].remove(context["Selected_Group"][0])
	context["Levels"] = Level_Groups[Selected_L_Group_Index]


	for Group in LG_1_Exercises:
		for x in Group:
		# for x in LG_1_Exercises[0]:
			Group_Index = LG_1_Exercises.index(Group)
			_Type = x[0]
			_Code = x[2]
			for n in range(1, 6):
				Level_Group_Index = n - 1
				Level_Num = n + Level_Constant
				# Input_Code = "L" + str(n) + x[2]
				# print(Input_Code)
				if Exercise.objects.filter(Type = _Type, Level = Level_Num).exists():
					_Exercise = Exercise.objects.get(Type = _Type, Level = Level_Num)
					x[1][n - 1] = _Exercise.Name
					if Group_Index == 0:
						context["Levels"][Level_Group_Index][2].append([_Exercise.Name, _Code])
					elif Group_Index == 1:
						context["Levels"][Level_Group_Index][3].append([_Exercise.Name, _Code])
					elif Group_Index == 2:
						context["Levels"][Level_Group_Index][4].append([_Exercise.Name, _Code])
					# print(_Exercise.Name)
				else:
					x[1][n - 1] = "Level " + str(n) + " Exercise"
					if Group_Index == 0:
						context["Levels"][Level_Group_Index][2].append(["Level " + str(Level_Num) + " Exercise", _Code])
					elif Group_Index == 1:
						context["Levels"][Level_Group_Index][3].append(["Level " + str(Level_Num) + " Exercise", _Code])
					elif Group_Index == 2:
						context["Levels"][Level_Group_Index][4].append(["Level " + str(Level_Num) + " Exercise", _Code])

	if request.GET.get("Update_Exercises"):
		for Group in LG_1_Exercises:
			for x in Group:
		# for x in LG_1_Exercises[0]:
				_Type = x[0]
				_ID = x[2]
				# print(_ID)
				for n in range(1, 6):
					Level_Num = n + Level_Constant
					Input_Code = "L" + str(Level_Num) + x[2]
					# print(Input_Code)
					if request.GET.get(Input_Code) != "" and request.GET.get(Input_Code) != None:
						_Name = request.GET.get(Input_Code)
						# print(Input_Code + " " + _Name)
						print(Input_Code + " : " + _Name)
						if Exercise.objects.filter(Type = x[0], Level = Level_Num).exists():
							print("Changing Exercise: " + _Name)
							_Exercise = Exercise.objects.get(Type = _Type, Level = Level_Num)
							_Exercise.Name = _Name
							_Exercise.Code = Input_Code
							_Exercise.save()
							print("New Name: " + _Exercise.Name)
						else:
							_Exercise = Exercise(Type = x[0], Level = Level_Num, Name = _Name, Code = Input_Code)
							_Exercise.save()
		return HttpResponseRedirect("/admin-exercises")

	context["Exercises_1"] = LG_1_Exercises[0]
	context["Exercises_2"] = LG_1_Exercises[1]
	context["Exercises_3"] = LG_1_Exercises[2]

	# context["Levels"] = [[1, []],[2, []],[3, []],[4, []],[5, []]]

	Exercises_List_1 = []

	for i in Exercise.objects.all():
		row = []
		row.append(i.Type)
		row.append(i.Level)
		row.append(i.Name)
		row.append(i.Bodyweight)
		# print(row)
		Exercises_List_1.append(row)


	return render(request, "admin_exercises.html", context)


@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Workouts(request):
	context = {}
	context["Users"] = []

	context["Exercise_Types"] = Exercise_Types

	context["Exercises"] = []
	context["Sets"] = []
	context["Workouts"] = []

	context["Member_Added"] = ""
	context["Exercise_Added"] = ""
	context["Set_Added"] = ""
	context["Workout_Added"] = ""

	context["Weeks"] = [["Week 1", "W1", 1, [[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]] ], 
	["Week 2", "W2", 2], 
	["Week 3", "W3", 3], 
	["Week 4", "W4", 4]]
	context["Days"] = [["Day 1", "D1", 1],
	["Day 2", "D2", 2],
	["Day 3", "D3", 3]]
	context["Sets_Per_Workout"] = [["Set 1", 1],
	["Set 2", 2],
	["Set 3", 3],
	["Set 4", 4],
	["Set 5", 5],
	["Set 6", 6],]

	context["Test_Dict"] = {"Test": "Dictionary Works"}

	context["Placeholders"] = [
	[[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]], 
	[[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]], 
	[[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]], 
	[[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]]]
	# Week - 0 to 3
	# Day - 0 to 2
	# Set - 0 to 5

	context["Workout_Templates"] = [
	["Week 1", [["Day 1", [[], [], [], [], [], []], "D1"], ["Day 2", [[], [], [], [], [], []], "D2"], ["Day 3", [[], [], [], [], [], []], "D3"]], "W1"], 
	["Week 2", [["Day 1", [[], [], [], [], [], []], "D1"], ["Day 2", [[], [], [], [], [], []], "D2"], ["Day 3", [[], [], [], [], [], []], "D3"]], "W2"], 
	["Week 3", [["Day 1", [[], [], [], [], [], []], "D1"], ["Day 2", [[], [], [], [], [], []], "D2"], ["Day 3", [[], [], [], [], [], []], "D3"]], "W3"], 
	["Week 4", [["Day 1", [[], [], [], [], [], []], "D1"], ["Day 2", [[], [], [], [], [], []], "D2"], ["Day 3", [[], [], [], [], [], []], "D3"]], "W4"]]


	context["Templates"] = []
	Weeks = [1, 2, 3, 4]
	Days = [1, 2, 3]
	
	for _Template in Workout_Template.objects.filter(Level_Group=1):
		Template_Dict = {}
		Template_Dict["Regular"] = ["True"]
		Button_Code = "W" + str(_Template.Week) + "D" + str(_Template.Day) + "_Update_Workout"
		Template_Dict["Button_Code"] = Button_Code

		Empty_Sets = 6 - _Template.SubWorkouts.all().count()

		if _Template.Alloy:
			Template_Dict["Regular"] = []
			Template_Dict["Alloy"] = ["True"]

		for N in _Template.SubWorkouts.all():
			Sub_Dict = {}
			Sub_Dict["Exercise_Type"] = [N.Exercise_Type, N.pk]
			Sub_Dict["Sets"] = [N.Sets, N.pk]
			Sub_Dict["Reps"] = [N.Reps, N.pk]
			Sub_Dict["RPE"] = [N.RPE, N.pk]
			Sub_Dict["Deload"] = [N.Deload, N.pk]
			Sub_Dict["Alloy"] = []

			if _Template.Alloy:
				Sub_Dict["Alloy"] = [N.Money, N.pk]

		context["Templates"].append(Template_Dict)

		if request.GET.get(Button_Code):
			print("BUTTON PRESSED")
			print(request.GET.keys())

	print("N Workouts: " + str(Workout_Template.objects.filter(Level_Group=1).count()))
	for i in Workout_Template.objects.filter(Level_Group=1):
		_week_index = i.Week - 1 #Workout_Templates[index]
		_day_index = i.Day - 1 #Workout_Templates[week][1][_day_index]	
		if i.Ordered_ID == 1:
			i.First = True
			i.save()
			# print("First Workout Template: " + str(i.Ordered_ID))	
		elif i.Ordered_ID == Workout_Template.objects.filter(Level_Group=1).count():
			i.Last = True
			i.save()
		# 	print("Last Workout Template: " + str(i.Ordered_ID))	
		# else:
		# 	print("Workout Template: " + str(i.Ordered_ID))	

		# i.Level_Group = 1
		# i.save()
		# print("Existing Workout Template: " + "Week " + str(i.Week) + " Day " + str(i.Day) + " Ordered ID: " + str(i.Ordered_ID) + " Level Group: " + str(i.Level_Group))
		Num_Sets = i.SubWorkouts.all().count()
		Empty_Sets = 6 - i.SubWorkouts.all().count()
		if i.Alloy:
			context["Workout_Templates"][_week_index][1][_day_index].append(["A"])
			context["Workout_Templates"][_week_index][1][_day_index].append([])
		else:
			context["Workout_Templates"][_week_index][1][_day_index].append([])
			context["Workout_Templates"][_week_index][1][_day_index].append(["R"])
		count = 0
		Filled_Subs = []
		for x in i.SubWorkouts.all():
			count += 1
			_exercise_type = x.Exercise_Type
			_sets = x.Sets
			_reps = x.Reps			
			_order = x.Order
			Filled_Subs.append(_order)
			# _order = str(count)
			print("Order: " + str(_order))
			if _order == "" or _order == None:
				print("Empty Order")
			# print(x.Exercise_Type + " " + str(x.Sets) + " x " + str(x.Reps)) + " (Set " + str(x.Order) + ")"
			_subworkout_index = x.Order - 1
			_rpe = ""
			_deload = ""
			_money = ""
			if x.RPE != 0:
				_rpe = x.RPE
			if x.Deload != 0:
				_deload = x.Deload
			if x.Money != 0 and x.Money != None:
				_money = str(x.Money) + "+" 
			context["Workout_Templates"][_week_index][1][_day_index][1][_subworkout_index] = [_exercise_type, str(_sets) + " x ", 
			_reps, "Set " + str(_order) + ":", _sets, _order, _rpe, _deload, _money]

		for y in range(1, 7):
			if y not in Filled_Subs:
				Empty_Index = y - 1
				context["Workout_Templates"][_week_index][1][_day_index][1][Empty_Index] = ["", "", "", "Set " + str(Empty_Index + 1) + ":", "", Empty_Index + 1, "", "", ""]

		# for y in range(1, Empty_Sets + 1):
		# 	Empty_Index = Num_Sets - 1 + y
			# context["Workout_Templates"][_week_index][1][_day_index][1][Empty_Index] = ["", "", "", "Set " + str(Empty_Index + 1) + ":", "", Empty_Index + 1, "", "", ""]

	for i in context["Weeks"]:
		for y in context["Days"]:
			btn_code = i[1] + y[1] + "_Update_Workout"
			_week = i[2]
			_day = y[2]
			if Workout_Template.objects.filter(Level_Group=1, Week=_week, Day=_day).exists() == False:
				print("Created Workout Template: " + str(_week) + str(_day))
				_Workout_Template = Workout_Template(Level_Group=1, Week=_week, Day=_day)
				_Workout_Template.Ordered_ID = (_week - 1)*3 + _day
				_Workout_Template.save()
			else:
				_Workout_Template = Workout_Template.objects.get(Level_Group=1, Week=_week, Day=_day)
				_Workout_Template.Ordered_ID = (_week - 1)*3 + _day
				_Workout_Template.save()
			if request.GET.get(btn_code):
				print(btn_code)
				print("Workout Type: " + request.GET["Type"])
				
				if request.GET["Type"] == "A":
					_Workout_Template.Alloy = True
					_Workout_Template.save()
				elif request.GET["Type"] == "R":
					_Workout_Template.Alloy = False
					_Workout_Template.save()

				for z in range(1,7):
					# if (_Workout_Template.SubWorkouts.all().filter(Order = z).exists()):
					# 	_Placeholder_SubWorkout = _Workout_Template.SubWorkouts.all().get(Order = z)
						
					# 	_Type = _Placeholder_SubWorkout.Exercise_Type
					# 	_Sets = _Placeholder_SubWorkout.Sets
					# 	_Reps = _Placeholder_SubWorkout.Reps
						# context["Placeholders"][_week - 1][_day - 1][z - 1] = [_Type, _Sets, _Reps]
					_sets = "Sets_" + str(z)
					_reps = "Reps_" + str(z)
					_type = "Type_" + str(z)					
					_rpe = "RPE_" + str(z)
					_deload = "Deload_" + str(z)
					_money = "Money_" + str(z)
					# print(request.GET[_type])
					if (request.GET.get(_type) != "" or (request.GET.get(_sets) != "" or request.GET.get(_reps) != ""
						or request.GET.get(_rpe) != "" or request.GET.get(_deload) != "" or request.GET.get(_money) != "")):
						# print(request.GET.get(_sets))
						# print(request.GET.get(_reps))
						# print(request.GET.get(_type))
						# print(request.GET.get(_rpe))
						# print(request.GET.get(_money))
						_Sets_ = request.GET.get(_sets)
						_Reps_ = request.GET.get(_reps)
						_Type_ = request.GET.get(_type)
						_RPE = request.GET.get(_rpe)
						_Deload = request.GET.get(_deload)
						_Money = ""
						if _money in request.GET.keys():
							_Money = request.GET[_money]
						_SubWorkout = SubWorkout(Exercise_Type = _Type_, Order = z)
						if _Sets_ != "":
							_SubWorkout.Sets = _Sets_
						if _Reps_ != "":
							_SubWorkout.Reps = _Reps_
						if _RPE != "":
							_SubWorkout.RPE = _RPE
						if _Deload != "":
							_SubWorkout.Deload = _Deload 
						if _Money != "":
							print("Money: " + _Money)
							_SubWorkout.Money = _Money
							_SubWorkout.Alloy = True
							_Workout_Template.Alloy = True

						if (_Workout_Template.SubWorkouts.all().filter(Order = z).exists()):
							# print("Exists")
							_Edit_SubWorkout = _Workout_Template.SubWorkouts.all().get(Order = z)
							_Edit_SubWorkout.Exercise_Type = _Type_
							if _Sets_ != "":
								_Edit_SubWorkout.Sets = _Sets_
							if _Reps_ != "":
								_Edit_SubWorkout.Reps = _Reps_
							if (_RPE != ""):
								_Edit_SubWorkout.RPE = _RPE
							if _Deload != "":
								_Edit_SubWorkout.Deload = _Deload 								
							if _Money != "":
								_Edit_SubWorkout.Money = _Money
								print("Edited Money: " + _Money)
								_Edit_SubWorkout.Alloy = True
								_Workout_Template.Alloy = True
							_Edit_SubWorkout.save()
							_Workout_Template.save()
						else:
							# if _Type_ != "":
							_SubWorkout.save()
							_Workout_Template.SubWorkouts.add(_SubWorkout)
							_Workout_Template.save()
						# _Workout_Template.SubWorkouts.add(_SubWorkout)
						# _Workout_Template.save()
					# else:
					# 	print(i[0] + " " + y[0] + " No set ")
				return HttpResponseRedirect("/admin-workouts")
	return render(request, "admin_workouts.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Workouts_2(request):
	context = {}
	context["Users"] = []

	context["Exercise_Types"] = Exercise_Types
	SubWorkouts = [[1], [2], [3], [4], [5], [6], [7]]
	context["Workout_Templates"] = [
	["Week 1", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W1", 1], 
	["Week 2", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W2", 2], 
	["Week 3", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W3", 3], 
	["Week 4", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3]], "W4", 4]]

	_Templates = Workout_Template.objects.filter(Level_Group=2)
	# for i in _Templates:
		# print("Level Group 2 Template: " + str(i.Week) + " " + str(i.Day))
		# for x in i.SubWorkouts.all():
			# print(x.Exercise_Type)
		# i.delete()
	for x in context["Workout_Templates"]:
		for z in x[1]:
			print(z)
			z.append([])
			z.append([])

	N_SubWorkouts = len(SubWorkouts)

	for i in context["Workout_Templates"]:
		_Max_Index = len(i)
		_Week = i[_Max_Index - 1]
		_Week_Code = i[_Max_Index - 2]
		for _D in i[1]:
			# print(i[0] + " " + _D[0])
			_D[1] = [[1], [2], [3], [4], [5], [6], [7]]
			_Day = _D[3]
			_Day_Code = _D[2]
			_Btn_Code = _Week_Code + _Day_Code + "_Update_Workout"
			if Workout_Template.objects.filter(Level_Group=2, Week=_Week, Day=_Day).exists() == False:
				_Template = Workout_Template(Level_Group=2, Week=_Week, Day=_Day)
				_Template.Ordered_ID = (_Week - 1)*4 + _Day
				_Template.save()
				# print("Created Workout Template: W" + str(_Week) + " D" + str(_Day) + " Ordered ID: " + str(_Template.Ordered_ID))
			else:
				_Template = Workout_Template.objects.get(Level_Group=2, Week=_Week, Day=_Day)
				_Template.Ordered_ID = (_Week - 1)*4 + _Day
				_Template.save()

			if _Template.Alloy:
				_D[4].append("R")
			else:
				_D[5].append("R")

				# print("Existing Workout Template: W" + str(_Template.Week) + " D" + str(_Template.Day) + " Ordered ID: " + str(_Template.Ordered_ID))
			_Template_Code = _Week_Code + _Day_Code + " " + str(_Template.Ordered_ID)
			# print(_D[1])
			# DISPLAY HANDLED HERE
			# print(_Template_Code)
			for _S in _D[1]:
				_Index = _D[1].index(_S)
				_Sub_Index = _Index + 1
				# _S.append(_Index + 1)
				# _S = [_Index + 1]
				# print(_Index)
				# _S[0] = (_Index + 1)
				# print(_S)
				_Template = Workout_Template.objects.get(Level_Group=2, Week=_Week, Day=_Day)
				if (_Template.SubWorkouts.all().filter(Order = _Sub_Index).exists()):
					_Sub = _Template.SubWorkouts.all().get(Order = _Sub_Index)
					# _S = [_Sub.Exercise_Type, _Sub.Sets, _Sub.RPE, _Sub.Deload, _Sub.Money]
					_S.append(_Sub.Exercise_Type)
					_S.append(_Sub.Sets)
					if _Sub.Special_Reps == "":
						_S.append(_Sub.Reps)
					else:
						_S.append(_Sub.Special_Reps)
					_S.append(_Sub.RPE)
					_S.append(_Sub.Deload)
					_S.append(_Sub.Money)
				else :
					_S = _S + ["", "", "", "", "", ""]
			for _S in _Template.SubWorkouts.all():
				print("Subworkout for: " + _Template_Code)

			if request.GET.get(_Btn_Code):
				print("Button Pressed for: " + _Template_Code)

				if request.GET["Type"] == "A":
					_Template.Alloy = True
					_Template.save()
				elif request.GET["Type"] == "R":
					_Template.Alloy = False
					_Template.save()
				
				for i in range(1, N_SubWorkouts + 1):					
					# print(i)
					_Sub_Index = i
					_Sets = "Sets_" + str(i)
					_Reps = "Reps_" + str(i)
					_Type = "Type_" + str(i)
					_RPE = "RPE_" + str(i)
					_Deload = "Deload_" + str(i)
					_Alloy = "Alloy_" + str(i)
					Type = request.GET[_Type] 
					Sets = request.GET[_Sets]
					Reps = request.GET[_Reps].split(',')					
					if (Type != "" and Sets != "" and Reps != ""):
						print (_Template_Code + " Subworkout Changed: " + str(i))
						# print(request.GET[_Type])
						RPE = request.GET[_RPE]
						Deload = request.GET[_Deload]
						Alloy = ""
						if _Alloy in request.GET.keys():
							Alloy = request.GET[_Alloy]
						if (_Template.SubWorkouts.all().filter(Order = _Sub_Index).exists()):
							print("Subworkout Exists")
							_Subworkout = _Template.SubWorkouts.all().get(Order = _Sub_Index)
							_Subworkout.Exercise_Type = Type
							_Subworkout.Sets = Sets
							if len(Reps) == 1:
								_Subworkout.Reps = Reps[0]
								_Subworkout.Special_Reps = ""
							else:
								_Subworkout.Special_Reps = ",".join(Reps)
							if RPE != "":
								_Subworkout.RPE = RPE
							if Deload != "":
								_Subworkout.Deload = Deload
							if Alloy != "":
								_Subworkout.Money = Alloy
								_Subworkout.Alloy = True
								_Template.Alloy = True
							print("New Subworkout Type: " + _Subworkout.Exercise_Type)
							_Subworkout.save()					
							_Template.save()		
						else:
							_Subworkout = SubWorkout(Order=_Sub_Index, Exercise_Type=Type, Sets=Sets, Reps=Reps)
							_Subworkout.save()
							if RPE != "":
								_Subworkout.RPE = RPE
							if Deload != "":
								_Subworkout.Deload = Deload
							if Alloy != "":
								_Subworkout.Money = Alloy
								_SubWorkout.Alloy = True
								_Template.Alloy = True
							_Subworkout.save()
							_Template.SubWorkouts.add(_Subworkout)
							_Template.save()
				return HttpResponseRedirect("/admin-workouts-2")
	# print(context["Workout_Templates"])		
	return render(request, "admin_workouts_2.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Workouts_3(request):
	context = {}
	context["Users"] = []

	context["Exercise_Types"] = Exercise_Types
	SubWorkouts = [[1], [2], [3], [4], [5], [6], [7]]

	context["Blocks"] = [["Block 1 - Volume", "Block_1", 1], ["Block 2 - Strength/Power", "Block_2", 2]]
	context["Selected_Block"] = [["Block 1 - Volume", "Block_1", 1]]	

	if "Selected_Block" in request.session.keys():
		_Selected_Block = context["Blocks"][request.session["Selected_Block"] - 1]
		context["Selected_Block"] = [_Selected_Block]
		context["Blocks"].remove(_Selected_Block)
	else:
		request.session["Selected_Block"] = 1
		_Selected_Block = context["Blocks"][request.session["Selected_Block"] - 1]
		context["Selected_Block"] = [_Selected_Block]
		context["Blocks"].remove(_Selected_Block)

	if request.method == 'POST':
		if request.POST['Block'] == "Block_1":
			request.session["Selected_Block"] = 1
		elif request.POST['Block'] == "Block_2":
			request.session["Selected_Block"] = 2
		return HttpResponseRedirect("/admin-workouts-3")

	context["Workout_Templates"] = []

	Templates = [
	[["Week 1", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W1", 1], 
	["Week 2", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W2", 2], 
	["Week 3", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W3", 3], 
	["Week 4", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W4", 4]],
	
	[["Week 1", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W1", 1], 
	["Week 2", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W2", 2], 
	["Week 3", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W3", 3], 
	["Week 4", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W4", 4],
	["Week 5", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3]], "W5", 5]]]

	for x in Templates:
		for n in x:
			for z in n[1]:
				print(z)
				z.append([])
				z.append([])


	context["Block_Label"] = context["Selected_Block"][0][0]
	# if request.session["Selected_Block"] == 1:
	# 	context["Block_Label"] = context["Blocks"][0][0]
	# elif request.session["Selected_Block"] == 2:
	# 	context["Block_Label"] = context["Blocks"][1][0]

	Selected_Block = request.session["Selected_Block"]
	if Selected_Block == 1:
		context["Workout_Templates"] = Templates[0]
	elif Selected_Block == 2:
		context["Workout_Templates"] = Templates[1]

	_Templates = Workout_Template.objects.filter(Level_Group=3, Block_Num=Selected_Block)

	for i in _Templates:
		print("Level Group 3 Template: " + str(i.Week) + " " + str(i.Day) + " Block #: " + str(i.Block_Num))
		for x in i.SubWorkouts.all():
			print("	" + x.Exercise_Type + " " + str(x.Sets) + " x " + str(x.Reps))
		# i.delete()
	N_SubWorkouts = len(SubWorkouts)
	# for _Templates in context["Workout_Templates"]:
	if (3 == 3):
		for i in context["Workout_Templates"]:
			_Max_Index = len(i)
			_Week = i[_Max_Index - 1]
			_Week_Code = i[_Max_Index - 2]
			for _D in i[1]:
				# print(i[0] + " " + _D[0])
				_D[1] = [[1], [2], [3], [4], [5], [6], [7]]
				_Day = _D[3]
				_Day_Code = _D[2]
				_Btn_Code = _Week_Code + _Day_Code + "_Update_Workout"
				if Workout_Template.objects.filter(Level_Group=3, Week=_Week, Day=_Day, Block_Num=Selected_Block).exists() == False:
					_Template = Workout_Template(Level_Group=3, Week=_Week, Day=_Day, Block_Num=Selected_Block)
					_Template.Ordered_ID = (_Week - 1)*4 + _Day
					_Template.save()
					# print("Created Workout Template: W" + str(_Week) + " D" + str(_Day) + " Ordered ID: " + str(_Template.Ordered_ID))
				else:
					_Template = Workout_Template.objects.get(Level_Group=3, Week=_Week, Day=_Day, Block_Num=Selected_Block)
					_Template.Ordered_ID = (_Week - 1)*4 + _Day
					_Template.save()

				if _Template.Alloy:
					_D[4].append("A")
				else:
					_D[5].append("R")

					# print("Existing Workout Template: W" + str(_Template.Week) + " D" + str(_Template.Day) + " Ordered ID: " + str(_Template.Ordered_ID))
				_Template_Code = _Week_Code + _Day_Code + " " + str(_Template.Ordered_ID)
				# print(_D[1])
				# DISPLAY HANDLED HERE
				print(_Template_Code)
				for _S in _D[1]:
					_Index = _D[1].index(_S)
					_Sub_Index = _Index + 1
					# _S.append(_Index + 1)
					# _S = [_Index + 1]
					# print(_Index)
					# _S[0] = (_Index + 1)
					print(_S)
					_Template = Workout_Template.objects.get(Level_Group=3, Week=_Week, Day=_Day, Block_Num=Selected_Block)
					if (_Template.SubWorkouts.all().filter(Order = _Sub_Index).exists()):
						_Sub = _Template.SubWorkouts.all().get(Order = _Sub_Index)
						# _S = [_Sub.Exercise_Type, _Sub.Sets, _Sub.RPE, _Sub.Deload, _Sub.Money]
						_S.append(_Sub.Exercise_Type)
						_S.append(_Sub.Sets)
						_S.append(_Sub.Reps)
						_S.append(_Sub.RPE)
						_S.append(_Sub.Deload)
						_S.append(_Sub.Money)
					else :
						_S = _S + ["", "", "", "", "", ""]
				for _S in _Template.SubWorkouts.all():
					print("Subworkout for: " + _Template_Code)

				if request.GET.get(_Btn_Code):
					print("Button Pressed for: " + _Template_Code)

					if request.GET["Type"] == "A":
						_Template.Alloy = True
						_Template.save()
					elif request.GET["Type"] == "R":
						_Template.Alloy = False
						_Template.save()

					for i in range(1, N_SubWorkouts + 1):					
						# print(i)
						_Sub_Index = i
						_Sets = "Sets_" + str(i)
						_Reps = "Reps_" + str(i)
						_Type = "Type_" + str(i)
						_RPE = "RPE_" + str(i)
						_Deload = "Deload_" + str(i)
						_Alloy = "Alloy_" + str(i)
						Type = request.GET[_Type] 
						Sets = request.GET[_Sets] 
						Reps = request.GET[_Reps] 					
						if (Type != "" and Sets != "" and Reps != ""):
							print (_Template_Code + " Subworkout Changed: " + str(i))
							# print(request.GET[_Type])
							RPE = request.GET[_RPE]
							Deload = request.GET[_Deload]
							Alloy = request.GET[_Alloy]
							if (_Template.SubWorkouts.all().filter(Order = _Sub_Index).exists()):
								_Subworkout = _Template.SubWorkouts.all().get(Order = _Sub_Index)
								_Subworkout.Type = Type
								_Subworkout.Sets = Sets
								_Subworkout.Reps = Reps
								if RPE != "":
									_Subworkout.RPE = RPE
								if Deload != "":
									_Subworkout.Deload = Deload
								if Alloy != "":
									_Subworkout.Money = Alloy
									_SubWorkout.Alloy = True
									_Template.Alloy = True
								_Subworkout.save()					
								_Template.save()		
							else:
								_Subworkout = SubWorkout(Order=_Sub_Index, Exercise_Type=Type, Sets=Sets, Reps=Reps)
								_Subworkout.save()
								if RPE != "":
									_Subworkout.RPE = RPE
								if Deload != "":
									_Subworkout.Deload = Deload
								if Alloy != "":
									_Subworkout.Money = Alloy
									_Subworkout.Alloy = True
									_Template.Alloy = True
								_Subworkout.save()
								_Template.SubWorkouts.add(_Subworkout)
								_Template.save()
					return HttpResponseRedirect("/admin-workouts-3")
	# print(context["Workout_Templates"])		
	return render(request, "admin_workouts_3.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Workouts_4(request):
	context = {}
	context["Users"] = []
	context["Exercise_Types"] = Exercise_Types
	SubWorkouts = [[1], [2], [3], [4], [5], [6], [7]]

	context["Blocks"] = [["Block 1 - Volume", "Block_1", 1], ["Block 2 - Strength/Power", "Block_2", 2]]
	context["Selected_Block"] = [["Block 1 - Volume", "Block_1", 1]]	

	if "Selected_Block" in request.session.keys():
		_Selected_Block = context["Blocks"][request.session["Selected_Block"] - 1]
		context["Selected_Block"] = [_Selected_Block]
		context["Blocks"].remove(_Selected_Block)
	else:
		request.session["Selected_Block"] = 1
		_Selected_Block = context["Blocks"][request.session["Selected_Block"] - 1]
		context["Selected_Block"] = [_Selected_Block]
		context["Blocks"].remove(_Selected_Block)

	if request.method == 'POST':
		if request.POST['Block'] == "Block_1":
			request.session["Selected_Block"] = 1
		elif request.POST['Block'] == "Block_2":
			request.session["Selected_Block"] = 2
		return HttpResponseRedirect("/admin-workouts-4")

	context["Workout_Templates"] = []

	Templates = [
	[["Week 1", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W1", 1], 
	["Week 2", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W2", 2], 
	["Week 3", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W3", 3], 
	["Week 4", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3]], "W4", 4]],
	
	[["Week 1", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W1", 1], 
	["Week 2", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W2", 2], 
	["Week 3", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3], ["Day 4", SubWorkouts, "D4", 4]], "W3", 3], 
	["Week 4", [["Day 1", SubWorkouts, "D1", 1], ["Day 2", SubWorkouts, "D2", 2], ["Day 3", SubWorkouts, "D3", 3]], "W4", 4]]]

	for x in Templates:
		for n in x:
			for z in n[1]:
				print(z)
				z.append([])
				z.append([])

	context["Block_Label"] = context["Selected_Block"][0][0]
	# if request.session["Selected_Block"] == 1:
	# 	context["Block_Label"] = context["Blocks"][0][0]
	# elif request.session["Selected_Block"] == 2:
	# 	context["Block_Label"] = context["Blocks"][1][0]

	Selected_Block = request.session["Selected_Block"]
	if Selected_Block == 1:
		context["Workout_Templates"] = Templates[0]
	elif Selected_Block == 2:
		context["Workout_Templates"] = Templates[1]

	_Templates = Workout_Template.objects.filter(Level_Group=4, Block_Num=Selected_Block)

	for i in _Templates:
		print("Level Group 4 Template: " + str(i.Week) + " " + str(i.Day) + " Block #: " + str(i.Block_Num))
		for x in i.SubWorkouts.all():
			print("	" + x.Exercise_Type + " " + str(x.Sets) + " x " + str(x.Reps))
		# i.delete()
	N_SubWorkouts = len(SubWorkouts)
	# for _Templates in context["Workout_Templates"]:
	if (3 == 3):
		for i in context["Workout_Templates"]:
			_Max_Index = len(i)
			_Week = i[_Max_Index - 1]
			_Week_Code = i[_Max_Index - 2]
			for _D in i[1]:
				# print(i[0] + " " + _D[0])
				_D[1] = [[1], [2], [3], [4], [5], [6], [7]]
				_Day = _D[3]
				_Day_Code = _D[2]
				_Btn_Code = _Week_Code + _Day_Code + "_Update_Workout"
				if Workout_Template.objects.filter(Level_Group=4, Week=_Week, Day=_Day, Block_Num=Selected_Block).exists() == False:
					_Template = Workout_Template(Level_Group=4, Week=_Week, Day=_Day, Block_Num=Selected_Block)
					_Template.Ordered_ID = (_Week - 1)*4 + _Day
					_Template.save()
					# print("Created Workout Template: W" + str(_Week) + " D" + str(_Day) + " Ordered ID: " + str(_Template.Ordered_ID))
				else:
					_Template = Workout_Template.objects.get(Level_Group=4, Week=_Week, Day=_Day, Block_Num=Selected_Block)
					_Template.Ordered_ID = (_Week - 1)*4 + _Day
					_Template.save()

				if _Template.Alloy:
					_D[4].append("A")
				else:
					_D[5].append("R")

				# if _Template.All

					# print("Existing Workout Template: W" + str(_Template.Week) + " D" + str(_Template.Day) + " Ordered ID: " + str(_Template.Ordered_ID))
				_Template_Code = _Week_Code + _Day_Code + " " + str(_Template.Ordered_ID)
				# print(_D[1])
				# DISPLAY HANDLED HERE
				print(_Template_Code)
				for _S in _D[1]:
					_Index = _D[1].index(_S)
					_Sub_Index = _Index + 1
					# _S.append(_Index + 1)
					# _S = [_Index + 1]
					# print(_Index)
					# _S[0] = (_Index + 1)
					print(_S)
					_Template = Workout_Template.objects.get(Level_Group=4, Week=_Week, Day=_Day, Block_Num=Selected_Block)
					if (_Template.SubWorkouts.all().filter(Order = _Sub_Index).exists()):
						_Sub = _Template.SubWorkouts.all().get(Order = _Sub_Index)
						# _S = [_Sub.Exercise_Type, _Sub.Sets, _Sub.RPE, _Sub.Deload, _Sub.Money]
						_S.append(_Sub.Exercise_Type)
						_S.append(_Sub.Sets)
						_S.append(_Sub.Reps)
						_S.append(_Sub.RPE)
						_S.append(_Sub.Deload)
						_S.append(_Sub.Money)
					else :
						_S = _S + ["", "", "", "", "", ""]
				for _S in _Template.SubWorkouts.all():
					print("Subworkout for: " + _Template_Code)

				if request.GET.get(_Btn_Code):
					if request.GET["Type"] == "A":
						_Template.Alloy = True
						_Template.save()
					elif request.GET["Type"] == "R":
						_Template.Alloy = False
						_Template.save()
					print("Button Pressed for: " + _Template_Code)
					for i in range(1, N_SubWorkouts + 1):					
						# print(i)
						_Sub_Index = i
						_Sets = "Sets_" + str(i)
						_Reps = "Reps_" + str(i)
						_Type = "Type_" + str(i)
						_RPE = "RPE_" + str(i)
						_Deload = "Deload_" + str(i)
						_Alloy = "Alloy_" + str(i)
						Type = request.GET[_Type] 
						Sets = request.GET[_Sets] 
						Reps = request.GET[_Reps] 					
						if (Type != "" and Sets != "" and Reps != ""):
							print (_Template_Code + " Subworkout Changed: " + str(i))
							# print(request.GET[_Type])
							RPE = request.GET[_RPE]
							Deload = request.GET[_Deload]
							Alloy = ""
							if _Alloy in request.GET.keys():
								Alloy = request.GET[_Alloy]
							if (_Template.SubWorkouts.all().filter(Order = _Sub_Index).exists()):
								_Subworkout = _Template.SubWorkouts.all().get(Order = _Sub_Index)
								_Subworkout.Type = Type
								_Subworkout.Sets = Sets
								_Subworkout.Reps = Reps
								if RPE != "":
									_Subworkout.RPE = RPE
								if Deload != "":
									_Subworkout.Deload = Deload
								if Alloy != "":
									_Subworkout.Money = Alloy
									_Subworkout.Alloy = True
									_Template.Alloy = True
								_Subworkout.save()					
								_Template.save()		
							else:
								_Subworkout = SubWorkout(Order=_Sub_Index, Exercise_Type=Type, Sets=Sets, Reps=Reps)
								_Subworkout.save()
								if RPE != "":
									_Subworkout.RPE = RPE
								if Deload != "":
									_Subworkout.Deload = Deload
								if Alloy != "":
									_Subworkout.Money = Alloy
									_SubWorkout.Alloy = True
									_Template.Alloy = True
								_Subworkout.save()
								_Template.SubWorkouts.add(_Subworkout)
								_Template.save()
					return HttpResponseRedirect("/admin-workouts-4")
	return render(request, "admin_workouts_4.html", context)
