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
import re
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
	["Medicine Ball", ["", "", "", "", ""], "MB"],
	["Carry", ["", "", "", "", ""], "CA"]
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
	if "Level_Group_Workout" not in request.session.keys():
		request.session["Level_Group_Workout"] = 1

	Level_Group_Dict = {"1-5": 1, "6-10": 2, "11-15": 3, "16-25": 4}

	Level_Group_Dict["1-5"] = 1
	Level_Group_Dict["6-10"] = 2
	Level_Group_Dict["11-15"] = 3
	Level_Group_Dict["16-25"] = 4

	Level_Group_List = [["1-5", 1], ["6-10", 2], ["11-15", 3], ["16-25", 4]]
	
	context["Blocks"] = [["Block 1 - Volume", "Block_1", 1], ["Block 2 - Strength/Power", "Block_2", 2]]
	context["Selected_Block"] = [["Block 1 - Volume", "Block_1", 1]]	

	context["Select_Left_Groups"] = []
	context["Selected_Group"] = []
	context["Select_Right_Groups"] = []

	context["Show_Blocks"] = []
	context["Show_Strength_Stop"] = []
	context["Show_Strength_Drop"] = []
	context["Blocks"] = [["Block 1 - Volume", "Block_1", 1], ["Block 2 - Strength/Power", "Block_2", 2]]
	context["Selected_Block"] = [["Block 1 - Volume", "Block_1", 1]]	

	if "Selected_Block" in request.session.keys():
		Selected_Block = context["Blocks"][request.session["Selected_Block"] - 1]
		context["Selected_Block"] = [Selected_Block]
		context["Blocks"].remove(Selected_Block)
	else:
		request.session["Selected_Block"] = 1
		Selected_Block = context["Blocks"][request.session["Selected_Block"] - 1]
		context["Selected_Block"] = [Selected_Block]
		context["Blocks"].remove(Selected_Block)


	for Group in Level_Group_List:
		if Group[1] < request.session["Level_Group_Workout"]:
			context["Select_Left_Groups"].append(Group)
		elif Group[1] == request.session["Level_Group_Workout"]:
			context["Selected_Group"] = Group
		elif Group[1] > request.session["Level_Group_Workout"]:
			context["Select_Right_Groups"].append(Group)

	if request.GET.get("Select_Level_Group"):
		print("Test")
		print("Selected Level Group: " + request.GET["Select_Level_Group"])
		Key = str(request.GET["Select_Level_Group"])
		print("Selected Group: " + request.GET["Select_Level_Group"])
		print(Level_Group_Dict.keys())

		print(Level_Group_Dict[Key])

		Selected_Group = request.GET["Select_Level_Group"]

		request.session["Level_Group_Workout"] = Level_Group_Dict[Key]
		print("Selected Group: " + str(request.session["Level_Group_Workout"]))
		return HttpResponseRedirect("/admin-workouts")
	print("New Selected Group: " + str(request.session["Level_Group_Workout"]))

	if request.GET.get("Block"):
		if request.GET['Block'] == "Block_1":
			request.session["Selected_Block"] = 1
		elif request.GET['Block'] == "Block_2":
			request.session["Selected_Block"] = 2
		return HttpResponseRedirect("/admin-workouts")

	Selected_Group = int(request.session["Level_Group_Workout"])

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

	context["Workout_Templates"] = [["Week 1", []], ["Week 2", []], ["Week 3", []], ["Week 4", []]]

	if Selected_Group < 3:
		Templates = Workout_Template.objects.filter(Level_Group = Selected_Group)
		Selected_Block_Num = 0
	else:
		context["Show_Strength_Stop"].append("True")
		context["Show_Blocks"].append("True")
		Templates = Workout_Template.objects.filter(Level_Group = Selected_Group, Block_Num=Selected_Block[2])
		Selected_Block_Num = Selected_Block[2]
		if Selected_Group == 4:
			context["Show_Strength_Drop"].append("True")
			New_Template, Created = Workout_Template.objects.get_or_create(Level_Group = Selected_Group, Block_Num = 2, Week = 4, Ordered_ID=16, Day = 4)
			New_Template.save()
		if Selected_Block_Num == 2:
			context["Workout_Templates"].append(["Week 5", []])
			for _Template in Workout_Template.objects.filter(Level_Group=Selected_Group, Block_Num=2, Week=5).all():
				_Template.delete()
			for n in range(3):
				print("N: " + str(n))
				Day = n + 1
				New_Template, Created = Workout_Template.objects.get_or_create(Level_Group = Selected_Group, Block_Num = 2, Week = 5, Ordered_ID=16 + Day, Day = Day)
				New_Template.save()
				# print(New_Template.)

	for i in Templates:
		print(i.Ordered_ID)
		Template_Dict = {}
		Button_Code = "W" + str(i.Week) + "D" + str(i.Day) + "_Update_Workout"
		Template_Dict["Day_Name"] = "Day " + str(i.Day)
		Template_Dict["Button_Code"] = Button_Code
		Template_Dict["Subs"] = []
		Template_Dict["Alloy"] = []
		Template_Dict["Regular"] = []
		Template_Dict["Line_Break"] = []
		if i.Day == 2:
			Template_Dict["Line_Break"].append("True")
		Num_Sets = i.SubWorkouts.all().count()
		Empty_Sets = 6 - Num_Sets
		_week_index = i.Week - 1 
		count = 0
		for Sub in i.SubWorkouts.all():
			if Sub.Exercise_Type == "":
				Sub.delete()
			Sub_Dict = {}
			count += 1
			Sub.Order = count
			Sub.save()
			Sub_Dict["Order"] = Sub.Order
			Sub_Dict["Type"] = Sub.Exercise_Type
			Sub_Dict["Sets"] = Sub.Sets
			Sub_Dict["Reps"] = Sub.Reps
			Sub_Dict["RPE"] = Sub.RPE
			Sub_Dict["Deload"] = Sub.Deload
			Sub_Dict["Alloy_Reps"] = ""
			if Sub.Alloy_Reps != None and Sub.Alloy_Reps != 0:
				Sub_Dict["Alloy_Reps"] = Sub.Alloy_Reps
				Sub.Alloy = True
				Sub.save()
				i.Alloy = True
				i.save()
			Sub_Dict["Strength_Stop"] = Sub.Strength_Stop
			Sub_Dict["Strength_Drop"] = Sub.Strength_Drop
			Template_Dict["Subs"].append(Sub_Dict)
		if i.Alloy:
			Template_Dict["Alloy"].append("True")
		else:
			Template_Dict["Regular"].append("True")			
		for E in range(Empty_Sets):
			Empty_Dict = {}
			Empty_Dict["Order"] = Num_Sets + E + 1
			Template_Dict["Subs"].append(Empty_Dict)		
		if i.Ordered_ID == 1:
			i.First = True
			Template_Dict["Day_Name"] += " (First)"
			i.save()
		elif i.Ordered_ID == Workout_Template.objects.filter(Level_Group=Selected_Group).count():
			i.Last = True
			Template_Dict["Day_Name"] += " (Last)"
			i.save()
		if _week_index <= 4:			
			context["Workout_Templates"][_week_index][1].append(Template_Dict)
		# print(Button_Code)
		if request.GET.get(Button_Code):
			print("Line 455 Executing")
			if request.GET["Type"] == "A":
				i.Alloy = True
			elif request.GET["Type"] == "R":
				i.Alloy = False
			i.save()
			for Order in range(1, 7):
			# for Sub in i.SubWorkouts.all():
			# 	Order = Sub.Order
				Type_Code = "Type_" + str(Order)					
				Set_Code = "Sets_" + str(Order)
				Rep_Code = "Reps_" + str(Order)
				RPE_Code = "RPE_" + str(Order)
				Deload_Code = "Deload_" + str(Order)
				Alloy_Reps_Code = "Money_" + str(Order)				
				SS_Code = "SS_" + str(Order)
				if request.GET[Type_Code] != "":
					_Type = request.GET[Type_Code]
					_Sets = request.GET[Set_Code]
					_Reps = request.GET[Rep_Code]
					_RPE = request.GET[RPE_Code]
					_Deload = request.GET[Deload_Code]
					_Alloy_Reps = ""
					_SS = ""
					if Alloy_Reps_Code in request.GET.keys():
						_Alloy_Reps = request.GET[Alloy_Reps_Code]
					if SS_Code in request.GET.keys():
						_SS = request.GET[SS_Code]
						
					if (i.SubWorkouts.all().filter(Order = Order).exists()):
						_Edit_Sub = i.SubWorkouts.all().get(Order = Order)
						_Edit_Sub.Exercise_Type = _Type
						if _Sets != "":
							_Edit_Sub.Sets = _Sets
						if _Reps != "":
							_Edit_Sub.Reps = _Reps
						if _RPE != "":
							_Edit_Sub.RPE = _RPE
						if _Deload != "":
							_Edit_Sub.Deload = _Deload
						if _Alloy_Reps != "":
							_Edit_Sub.Alloy_Reps = _Alloy_Reps
							_Edit_Sub.Alloy = True
						if _SS != "":
							_Edit_Sub.Strength_Stop = _SS
							_Edit_Sub.Stop_Set = True							
						_Edit_Sub.save()
						i.save()
					else:
						New_Sub = SubWorkout_Template(Exercise_Type = _Type, Order = Order)
						if _Sets != "":
							New_Sub.Sets = _Sets
						if _Reps != "":
							New_Sub.Reps = _Reps
						if _RPE != "":
							New_Sub.RPE = _RPE
						if _Deload != "":
							New_Sub.Deload = _Deload
						if _Alloy_Reps != "":
							New_Sub.Alloy_Reps = _Alloy_Reps
							New_Sub.Alloy = True
						New_Sub.save()
						i.SubWorkouts.add(New_Sub)
						i.save()
			return HttpResponseRedirect("/admin-workouts")
	
	# Refresh_Context()	
	
	return render(request, "admin_workouts.html", context)


