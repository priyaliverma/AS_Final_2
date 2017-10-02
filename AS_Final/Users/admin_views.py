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
from checks import Admin_Check

Level_Group_1_Exercises = [["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat"], 
["LB Uni Push", "Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4"]]

def Copy_Exercises():
	f = open("Exercises.txt", "w+")
	for E in Exercise.objects.all():
		String = E.Type + "," + str(E.Level) + "," + E.Name + "\n"
		f.write(String)
	f.close()

def Recreate_Exercises():
	r = open("Imported_Exercises.txt", "r")
	l = r.readlines()
	for line in l:
		List = line.split(",")
		_Level = int(List[1])
		_Exercise, Created = Exercise.objects.get_or_create(Level = _Level, Type=List[0])
		_Exercise.Name = List[2]
		_Exercise.save()
	r.close()

def Update_Tempo_Pause():
	for E in Exercise.objects.all():
		L_Group = (Exercise.Level - (Exercise.Level % 5))/5
		if "Pause" in Exercise.Name:
			print(Pause_Dict[L_Group])
			E.Pause = Pause_Dict[L_Group]
		elif "Tempo" in Exercise.Name:
			print(Tempo_Dict[L_Group])
			E.Tempo_Value = Tempo_Dict[L_Group]

@user_passes_test(Admin_Check, login_url="/admin-login")
def AdminExercises(request):
	# Update_Tempo_Pause()	
	# Recreate_Exercises()
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
					# if Exercise.objects.filter(Type=_Type, Level=Level_Num).count() > 1:
					# 	Exercise.objects.filter(Type=_Type, Level=Level_Num)[0].delete()
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
					# x[1][n - 1] = "Level " + str(n) + " Exercise"
					x[1][n - 1] = "None"
					if Group_Index == 0:
						# context["Levels"][Level_Group_Index][2].append(["Level " + str(Level_Num) + " Exercise", _Code])
						context["Levels"][Level_Group_Index][2].append(["No Exercise", _Code])
					elif Group_Index == 1:
						# context["Levels"][Level_Group_Index][2].append(["Level " + str(Level_Num) + " Exercise", _Code])
						context["Levels"][Level_Group_Index][3].append(["No Exercise", _Code])
					elif Group_Index == 2:
						# context["Levels"][Level_Group_Index][2].append(["Level " + str(Level_Num) + " Exercise", _Code])
						context["Levels"][Level_Group_Index][4].append(["No Exercises", _Code])

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
						# print(Input_Code + " : " + _Name)
						if Exercise.objects.filter(Type = x[0], Level = Level_Num).exists():
							print("Changing Exercise: " + _Name)
							_Exercise = Exercise.objects.get(Type = _Type, Level = Level_Num)
							_Exercise.Name = _Name
							_Exercise.Code = Input_Code
							_Exercise.save()
							# print("New Name: " + _Exercise.Name)
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

def Copy_Workouts():
	f = open("Workouts.txt", "w+")
	f.write("Subworkout Format: Order,Type,Sets,Reps,Deload,Alloy_Reps,Stop,Drop")
	for W in Workout_Template.objects.all():
		# Use this to match to current workouts using object.get
		Workout_String = "L" + str(W.Level_Group) + "W" + str(W.Week) + "D" + str(W.Day) + "B" + str(W.Block_Num)
		if W.Alloy:
			Workout_String += "A"
		else:
			Workout_String += "R"
		Workout_String += "|"
		print("Writing Template String: " + Workout_String)
		for S in W.SubWorkouts.all():
			Sub_String = "/"
			Sub_String += str(S.Order) + ","		
			Sub_String += S.Exercise_Type + ","		
			Sub_String += str(S.Sets) + ","		
			Sub_String += str(S.Reps) + ","		
			Sub_String += str(S.Deload) + ","		
			Sub_String += str(S.Alloy_Reps) + ","		
			Sub_String += str(S.Strength_Stop) + ","		
			Sub_String += str(S.Strength_Drop)		
			Workout_String += Sub_String
		Workout_String += "\n"
		f.write(Workout_String)
	f.close()

def Recreate_Workouts():
	r = open("Imported_Workouts.txt", "r")
	l = r.readlines()
	for line in l:
		line_list = line.split("|")
		Group = line_list[0][1]
		Week = line_list[0][3]
		Day = line_list[0][5]
		Block = line_list[0][7]
		print("Group " + Group + " Block " + Block + " Week " + Week + " Day " + Day)
		_Related_Workout = Workout_Template.objects.get(Level_Group = int(Group), Block_Num=int(Block), Week=int(Week), Day=int(Day))
		print(str(_Related_Workout) + " " + str(_Related_Workout.SubWorkouts.all().count()))
		print("Reading line: " + line)
		Sub_List = line_list[1].split("/")
		_Related_Workout.SubWorkouts.all().delete()
		if True:
			for Sub in Sub_List:
				if Sub != "":
					_List = Sub.split(",")
					if len(_List) > 5:
						_Sub_Template = SubWorkout_Template()
						if _List[0] != "":
							_Sub_Template.Order = int(_List[0])
						if _List[1] != "":
							_Sub_Template.Exercise_Type = _List[1]
						if _List[2] != "":
							_Sub_Template.Sets = int(_List[2])
						if _List[3] != "":
							_Sub_Template.Reps = _List[3]
						if _List[4] != "":
							_Sub_Template.Deload = int(_List[4])
						if _List[5] != "":
							_Sub_Template.Alloy_Reps = int(_List[5])
						if _List[6] != "":
							_Sub_Template.Strength_Stop = int(_List[6])
						if _List[7] != "":
							_Sub_Template.Strength_Drop = int(_List[7])
						if _List[8] != "":
							_Sub_Template.RPE = _List[8]
						_Sub_Template.save()
						_Related_Workout.SubWorkouts.add(_Sub_Template)



@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Workouts(request):
	# Recreate_Workouts()
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
		# print("Test")
		# print("Selected Level Group: " + request.GET["Select_Level_Group"])
		Key = str(request.GET["Select_Level_Group"])
		# print("Selected Group: " + request.GET["Select_Level_Group"])
		# print(Level_Group_Dict.keys())

		# print(Level_Group_Dict[Key])

		Selected_Group = request.GET["Select_Level_Group"]

		request.session["Level_Group_Workout"] = Level_Group_Dict[Key]
		# print("Selected Group: " + str(request.session["Level_Group_Workout"]))
		return HttpResponseRedirect("/admin-workouts")
	# print("New Selected Group: " + str(request.session["Level_Group_Workout"]))

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
			New_Template, Created = Workout_Template.objects.get_or_create(Level_Group = Selected_Group, Block_Num = 1, Week = 4, Ordered_ID=16, Day = 4)
			New_Template.save()
			New_Template, Created = Workout_Template.objects.get_or_create(Level_Group = Selected_Group, Block_Num = 2, Week = 4, Ordered_ID=16, Day = 4)
			New_Template.save()
		if Selected_Block_Num == 2:
			context["Workout_Templates"].append(["Week 5", []])

	for i in Templates:
		# print(i.Ordered_ID)
		Template_Dict = {}
		Button_Code = "W" + str(i.Week) + "D" + str(i.Day) + "_Update_Workout"
		print(Button_Code + str(i.Ordered_ID))
		Template_Dict["Day_Name"] = "Day " + str(i.Day)
		Template_Dict["Button_Code"] = Button_Code
		Template_Dict["Subs"] = []
		Template_Dict["Alloy"] = []
		Template_Dict["Regular"] = []
		Template_Dict["Line_Break"] = []
		if i.Day == 2:
			Template_Dict["Line_Break"].append("True")
		Num_Sets = i.SubWorkouts.all().count()
		Empty_Sets = 7 - Num_Sets
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
		else:
			i.First = False
		if i.Ordered_ID == Templates.count():
			if i.Block_Num == 1:
				i.Block_End = True
				i.Last = False
				Template_Dict["Day_Name"] += " (Block End)"
			else:
				i.Last = True
				i.Block_End = False
				Template_Dict["Day_Name"] += " (Last)"
		else:
			i.Last = False
			i.Block_End = False
		i.save()
		# Template_Dict["Day_Name"] += " " + str(i.Ordered_ID)
		# if _week_index <= 4:			
		# 	context["Workout_Templates"][_week_index][1].append(Template_Dict)
		context["Workout_Templates"][_week_index][1].append(Template_Dict)

		# print(Button_Code)
		if request.GET.get(Button_Code):
			print(Button_Code + " Pressed")
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
				SD_Code = "SD_" + str(Order)
				if request.GET[Type_Code] != "":
					_Type = request.GET[Type_Code]
					_Sets = request.GET[Set_Code]
					_Reps = request.GET[Rep_Code]
					_RPE = request.GET[RPE_Code]
					_Deload = request.GET[Deload_Code]
					_Alloy_Reps = ""
					_SS = ""
					_SD = ""
					if Alloy_Reps_Code in request.GET.keys():
						_Alloy_Reps = request.GET[Alloy_Reps_Code]
					if SS_Code in request.GET.keys():
						_SS = request.GET[SS_Code]
					if SD_Code in request.GET.keys():
						_SD = request.GET[SD_Code]

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
						# ALLOY
						if _Alloy_Reps != "":
							_Edit_Sub.Alloy_Reps = _Alloy_Reps
							_Edit_Sub.Alloy = True
						if _Alloy_Reps == "0" or _Alloy_Reps == 0:
							_Edit_Sub.Alloy = False
						# STRENGTH STOP
						if _SS != "":
							_Edit_Sub.Strength_Stop = _SS
							_Edit_Sub.Stop_Set = True				
						if _SS == "0" or _SS == 0:			
							_Edit_Sub.Stop_Set = False				
						# STRENGTH DROP
						if _SD != "":
							_Edit_Sub.Strength_Drop = _SD
							_Edit_Sub.Drop_Set = True				
						if _SD == "0" or _SD == 0:			
							_Edit_Sub.Drop_Set = False				
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
