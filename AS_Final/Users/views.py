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


@user_passes_test(User_Check, login_url="/")
def Contact_And_Support(request): 
	return render(request, "contact.html")

@user_passes_test(User_Check, login_url="/")
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
		Sub_Dict = {}
		Sub_Dict["Number_Sets"] = i.Sets
		Sub_Dict["Sets"] = []
		Sub_Dict["Type"] = i.Exercise_Type
		Sub_Dict["Exercise_Name"] = i.Exercise.Name
		Sets_List = i.Set_Stats.split("/")
		Sets_List.remove("")
		for Set in Sets_List:
			print("Set: " + str(Set))
			# if Set != "":
			Set_Dict = {}
			Set_Dict["Set_String"] = Set
			Set_Dict["Code"] = Set[0]
			Set_List = Set.split(",")
			Type_Code = Set_List[0]
			Set_Number = Set_List[0][1]
			if Type_Code == "A" + str(i.Sets):
				Set_Dict["Type"] = "Alloy"
				Type = "(Alloy)"
			else:
				Set_Dict["Type"] = "Regular"
				Type = "(Regular)"

			Reps = Set_List[1]
			Weight = Set_List[2]
			RPE = Set_List[3]
			Tempo = Set_List[4]
			Set_Dict["Set_Info"] = "Set " + Set_Number + ": " + Weight + " lbs, " + Reps + " reps @ " + RPE + " RPE "
			if Set[0] != "B":
				Sub_Dict["Sets"].append(Set_Dict)
		context["Patterns"].append(Sub_Dict)

	return render(request, "userprofile_view_workout.html", context)

@user_passes_test(User_Check, login_url="/")
def User_Profile(request):
	context = {}
	_User = request.user
	context["Username"] = _User.username
	_Member = Member.objects.get(User=_User)
	print("Testing print")

	if _User.username == "Test":
		_Member.Admin = True
		_Member.save()
	if _Member.Admin:
		print("You are admin!")
	else:
		print("Regular User")

	print(_Member.Level)
	context["Level"] = _Member.Level
	if request.method == "POST":
		P_1 = request.POST["Password_1"]
		P_2 = request.POST["Password_2"]
		if P_1 != "" and P_2 != "":
			_User.set_password(P_1)
			_User.save()
	return render(request, "userprofile.html", context)

@user_passes_test(User_Check, login_url="/")
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
		_Exercise = Exercise.objects.get(Type=i.Type, Level=_Member.Level)
		print("Stat: " + i.Type)
		context["Stats"].append([i.Type, i.Type, i.Max])

	_Workouts = _Member.workouts.all()

	context["Completed_Workouts"] = []
	for W in _Workouts:
		_Date = datetime.strptime(W._Date, "%m/%d/%Y")

		if W.Completed and _Date >= datetime.now() - timedelta(days=30):
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


def Logout(request):
	logout(request)
	return HttpResponseRedirect("/")

@user_passes_test(User_Check, login_url="/")
def Exercise_Descriptions(request):
	context = {}
	return render(request, "exercise_descriptions.html", context)

@user_passes_test(User_Check, login_url="/")
def Tutorial(request):
	context = {}
	return render(request, "tutorial.html", context)

@user_passes_test(User_Check, login_url="/")
def User_Page_Alloy(request):
	context = {}
	return render(request, "userpage_alloy.html", context)

@user_passes_test(User_Check, login_url="/")
def User_Page_Test(request): 
	_User = request.user
	_Member = Member.objects.get(User = _User)
	# workout_date_list = Workout.objects.filter(Member=_Member, Current_Block=True, Completed=False).values_list('_Date', flat=True).distinct()
	context = {}
	final_list = []

	_Date = datetime.now().strftime("%m/%d/%Y")

	if "Calendar_Date" in request.session.keys():
		print(request.session["Calendar_Date"])
		_Date = request.session["Calendar_Date"]
	else:
		request.session["Calendar_Date"] = datetime.now().strftime("%m/%d/%Y")

	_Date = request.session["Calendar_Date"]
	context["Date"] = _Date

# 	CALENDAR STUFF HERE
	# for workout_date in workout_date_list:
	# 	parsed_date_list = workout_date.split('/')
	# 	parsed_date_dict = {}
	# 	if (len(parsed_date_list) == 3): 
	# 		parsed_date_dict[str('month')] = str(parsed_date_list[0])
	# 		parsed_date_dict[str('day')] = str(parsed_date_list[1])
	# 		parsed_date_dict[str('year')] = str(parsed_date_list[2])
	# 		final_list.append(parsed_date_dict)

	context['final_list'] = json.dumps(final_list)

	if request.method == "POST":
		print("905 Redirecting")
		return HttpResponseRedirect("/userpage")

	return render(request, "userpage.html", context)


@user_passes_test(User_Check, login_url="/")
def User_Page(request): 
	_User = request.user
	_Member = Member.objects.get(User = _User)
	workout_date_list = Workout.objects.filter(Member=_Member, Current_Block=True, Completed=False).values_list('_Date', flat=True).distinct()
	context = {}
	final_list = []
	context["Patterns"] = []
	context["Workout_Day"] = [[], []]	
	context["Workout_Day_Time"] = [[], [], []]
	context["Tempo"] = []
	context["Workout_Stats"] = []
	context["Workout_Info"] = ""
	context["Alloy"] = ""
	context["First_Name"] = _User.first_name 
	context["Safe_Test"] = "<b> P Tag Test </B> Test "
	# Reversed_RPE = reversed(RPEs)
	# RPEs.reverse()
	context["RPE_List"] = RPEs

	_Date = datetime.now().strftime("%m/%d/%Y")
	# print("Today's Date: " + _Date)
	_Stats = _Member.Stats.all()

	# if "Calendar_Date" in request.session.keys():
	# 	print(request.session["Calendar_Date"])
	# 	_Date = request.session["Calendar_Date"]
	# else:
	# 	request.session["Calendar_Date"] = datetime.now().strftime("%m/%d/%Y")

	_Date = request.session["Calendar_Date"]

	Workout_Day = False
	Alloy_Workout = False
	Show_Alloy = False

	Requires_Tempo = False
	Alloys_Complete = True

	if request.GET.get("Level_Up_Check"):
		print("Level Up Check")
		Check_Level_Up(_Member)
	if True:
		if Workout.objects.filter(_Date=_Date, Member=_Member, Completed=False).exists():
			# if len(Workout.objects.filter(_Date=_Date, Member=_Member)) > 1:
			# 	for n in range(len(Workout.objects.filter(_Date=_Date, Member=_Member)) - 1):
			# 		Workout.objects.filter(_Date=_Date, Member=_Member)[0].delete()
			_Workout = Workout.objects.get(_Date=_Date, Member=_Member, Completed=False)
			Workout_Day = True

			context["Workout_Info"] = "Level " + str(_Workout.Level) + ", Week " + str(_Workout.Template.Week) + ", Day " + str(_Workout.Template.Day)
			
			if _Workout.Template.Alloy:
				Alloy_Workout = True
				if _Workout.Show_Alloy_Weights:
					Show_Alloy = True
				context["Alloy"] = "(Alloy)"
			for _Sub in _Workout.SubWorkouts.all():
				_Sub.Exercise, Created = Exercise.objects.get_or_create(Type=_Sub.Template.Exercise_Type, Level=_Workout.Level)
				_Sub.save()
				if _Sub.Exercise.Tempo or "Tempo" in _Sub.Exercise.Name:
					Requires_Tempo = True
			Workout_Date = datetime.strptime(_Workout._Date, "%m/%d/%Y")
		else:
			context["Workout_Day"][1].append("Y")
			context["Workout_Info"] = "No Workout For This Day"

	Show_Alloy = False

# 	WORKOUT DAY STUFF STARTS HERE
	if Workout_Day and True:
		# print("This Shouldn't Execute")
		_Workout = Workout.objects.get(_Date=_Date, Member=_Member, Completed=False)

		context["Workout_Stats"].append(_Workout.Level)
		context["Workout_Stats"].append(_Workout.Template.Week)
		context["Workout_Stats"].append(_Workout.Template.Day)

		if Requires_Tempo:
			context["Tempo"].append("Yes")
		if Show_Alloy:
			context["Show_Submit"] = ["Show"]
			context["Show_Get_Alloy"] = []
		else:
			context["Show_Submit"] = ["Show"]
			context["Show_Get_Alloy"] = ["Show"]
		Workout_Date = datetime.strptime(_Workout._Date, "%m/%d/%Y")

		Same_Day = False
		Past = False
		Future = False

		Get_Alloy_Pressed = False
		Get_Set_SS = False
		Get_Set_SD = False
# 		TIME-CHECK HERE
		if Workout_Date.strftime("%y/%m/%d") == datetime.now().strftime("%y/%m/%d"):
			print("Same Date")
			context["Workout_Day_Time"][1].append("True")
			Same_Day = True
		elif Workout_Date < datetime.now():
			context["Workout_Day_Time"][0].append("True")
			Past = True
			print("PAST IS TRUE")
		elif Workout_Date > datetime.now():
			Future = True
# 		FOR TESTING:
		Same_Day = True
		Past = False
		Future = False
		context["Workout_Day_Time"][1] = ["True"]
# 		SUB-WORKOUT LOOP
		for i in _Workout.SubWorkouts.all():
			Special_Sets = False
			StrengthStop = False
			StrengthDrop = False
			# print("Subworkout")
			# Check subworkout type here
			# Check for special sets here
			Special_Sets = False
			if i.Template.Special_Reps != "":
				Sets = i.Template.Special_Reps.split(",")
				Num_Special_Sets = len(Sets)
				Special_Sets = True
				
			# GETTING WEIGHTS FOR FIRST COLUMN
			# Check special subworkouts here
			_Stat, Created = Stat.objects.get_or_create(Type=i.Template.Exercise_Type, Member=_Member)		
			Alloy_Sub = False
			Row = {}
			Row["Money"] = ""
			if i.Template.Strength_Stop != 0:
				StrengthStop = True
				if not i.Stopped and not i.Maxed_Sets:
					Row["Strength_Stop"] = [i.Template.Strength_Stop]
					Row["Strength_Drop"] = []
			elif i.Template.Strength_Drop != 0:
				Row["Strength_Drop"] = [i.Template.Strength_Drop]
				Row["Strength_Stop"] = []
				StrengthDrop = True
			else:
				Row["Strength_Stop"] = []
				Row["Strength_Drop"] = []

			Set_Loop = i.Template.Sets
			
			Set_List = i.Set_Stats.split("/")
			if "" in Set_List:
				Set_List.remove("")
			Row["Set_Stats"] = str(Set_List)

			Num_Filled_Sets = 0

			Row["Filled_Sets"] = []

			Filled_Sets = []

			Row["Filled_Alloy"] = []

			# FILLED SETS CREATED HERE
# 			CHECK FOR NUMBER OF UNFILLED SETS
			for Set in Set_List:
				# print("Set in Set List")
				if Set != "":
					if Set[0][0] == "B":
						Row["Set_Stats"] += Set.split(",")[0]
						First_Empty_Set_Num = Set.split(",")[0][1]
						Num_Filled_Sets = int(First_Empty_Set_Num) - 1
						break 
					elif Set[0][0] == "R" or  Set[0][0] == "A":
						Filled_Sets.append(Set)

			Filled_Set_String = "/".join(Filled_Sets)

			# RESET
			i.Set_Stats = ""
			Reset_Sets = []
			for n in range(i.Template.Sets):				
				Reset_Sets.append("B" + str(n + 1) + ",,,,")
				# Reset_Sets.append("R" + str(n + 1) + ",,,,")

			i.Filled_Sets = len(Filled_Sets)

			# i.Set_Stats = "/".join(Reset_Sets)
			i.Set_Stats = "/".join(Filled_Sets)
			i.save()

			Num_Filled_Sets = len(Filled_Sets)

# 			FILLED SETS GET ADDED HERE
			for n in range(Num_Filled_Sets):
				# Row["Set_Stats"] += " Filled Set Test: " + str(Set)
				# Row["Set_Stats"] += ", Filled Set: " + str(n)
				# Row["Set_Stats"] += str([Set_List[n].split(",")])
				Set_Info = Set_List[n].split(",")
				if Set_Info != "" and len(Set_Info) >= 5:
					Filled_Set = {}
					Filled_Set["Reps"] = Set_Info[1] + " (Completed)"
					Filled_Set["Weight"] = Set_Info[2]  
					Filled_Set["RPE"] = Set_Info[3]
					Filled_Set["Tempo"] = Set_Info[4] 
					if Set_Info[0] == "A" + str(i.Template.Sets):
						Filled_Set["Reps"] = Set_Info[1]
						if i.Alloy_Passed:
							Filled_Set["Alloy_Passed"] = "(Passed)"
						else:
							Filled_Set["Alloy_Failed"] = "(Failed)"
						Row["Filled_Alloy"].append(Filled_Set)
					else:
						Row["Filled_Sets"].append(Filled_Set)
					Set_Loop -= 1

			# Row["Set_Stats"] = ""
# 			ALLOY SUBWORKOUT CASE HERE
			if Alloy_Workout and i.Template.Money != 0 and i.Template.Money != None:
				Alloy_Sub = True
				Row["Money"] = i.Template.Money
				_Stat.Alloy_Reps = i.Template.Money
				_Stat.save()
#			SUBWORKOUT ROW CONTEXT HERE 
			Row["Exercise_Type"] = i.Template.Exercise_Type
			Row["Exercise_Name"] = i.Exercise.Name
			Row["Sets"] = i.Template.Sets
			Reps = i.Template.Reps
			if re.search("-", i.Template.Reps) != None:
				Special_Sets = True
				i.Special_Sets = True
				i.save()
				Rep_String = i.Template.Reps.replace("-", ", ")
				Set_Rep_List = i.Template.Reps.split("-")				
				Row["Reps"] = Rep_String
				Row["Sets_Reps"] = str(i.Template.Sets) + " Sets (" + Rep_String + ") @ " + str(i.Template.RPE) + " RPE"
			else:
				Row["Reps"] = i.Template.Reps
				Row["Sets_Reps"] = str(i.Template.Sets) + " x " + str(i.Template.Reps) + " @ " + str(i.Template.RPE) + " RPE"

			Row["RPE"] = i.Template.RPE
			Row["Video_PK"] = []
			Row["Input_ID"] = i.Template.Exercise_Type + "_Input"
			if (i.Exercise.Video != None):
				_PK = i.Exercise.Video.pk
				Row["Video_PK"].append(_PK)


			BodyWeight = False
			if i.Template.Reps == "" or i.Template.Reps == "B":
				Row["Suggested_Weight"] = "Bodyweight"
				Row["Sets_Reps"] = str(i.Template.Sets) + " Sets " + " @ " + str(i.Template.RPE) + " RPE"
				Row["Reps"] = "Bodyweight"
				BodyWeight = True
			else:
				Row["Suggested_Weight"] = "Weight:"

# 			DETERMINING WEIGHT HERE
			Weight_String = ""
			if _Stat.Max != 0 and i.Template.Reps != "" and i.Template.Reps != "B":
				if len(i.Template.RPE) == 1:
					_RPE = int(i.Template.RPE) 
				elif len(i.Template.RPE) == 3 and i.Template.RPE[1] == "-":
					_RPE = int(i.Template.RPE[0])
				else:
					_RPE = 1

				if i.Template.Reps != "B":
					if Special_Sets:
						Estimate = Get_Weight(_Stat.Max, int(Set_Rep_List[1]), _RPE)						
					else:
						Estimate = Get_Weight(_Stat.Max, int(i.Template.Reps), _RPE)			

				Weight_Origin = str(_Stat.Max) + " " + str(i.Template.Reps) + " " + str(_RPE)
				
				Range_Min = Estimate - (Estimate % 5)
				Range_Max = Range_Min + 5
				
				i.Suggested_Weight = Range_Min
				i.save()
				# FOR TESTING
				if StrengthStop and i.Dropped:
					i.Suggested_Weight = Range_Min*(0.93)
					i.save()
				# REAL
				if StrengthDrop and i.Dropped:
					i.Suggested_Weight = Range_Min*(100 - i.Template.Strength_Drop)/100
					i.save()

				Weight_String = str(i.Suggested_Weight) + "-" + str(Range_Max) + " lbs" 
				Row["Suggested_Weight"] = "Weight: " + Weight_String + " " + Weight_Origin
				# _Stat.Suggested_Weight = Range_Min
				# _Stat.save()

			Row["Deload"] = "None"

			if i.Template.Deload != 0 and i.Template.Deload != None:
				Row["Deload"] = i.Template.Deload


			Row["Weight_Col"] = [[], [], []]
			Row["Reps_Col"] = [[], [], []]
			Row["RPE_Col"] = [[], [], []]
			Row["Tempo_Col"] = [[], [], []]
			Row["Same_Day_Col"] = {}

			Row["Same_Day_Col"]["Post_Show"] = {}

			Row["Same_Day_Col"]["Post_Show"]["Regular"] = []
			Row["Same_Day_Col"]["Post_Show"]["Alloy_Sub"] = []
			Row["Same_Day_Col"]["Post_Show"]["Alloy_Set"] = []

			Row["Same_Day_Col"]["Pre_Show"] = {}
			Row["Same_Day_Col"]["Pre_Show"]["Regular"] = []
			Row["Same_Day_Col"]["Pre_Show"]["Alloy_Sub"] = []
			Row["Same_Day_Col"]["Pre_Show"]["Alloy_Set"] = []


			Row["Tempo"] = []
			Row["Changeable"] = {"Yellow": [], "Normal" : []}
			Row["Non_Changeable"] = {"Yellow": [], "Normal" : []}

			Sub_Tempo = False

			if Requires_Tempo and "Tempo" in i.Exercise.Name:
				Sub_Tempo = True
				Row["Tempo"].append("Y")

			Row["Empty_Sets"] = []
			# We need to know:
				# If Alloy
			Set_Scheme = []

			if Alloy_Sub:
				Set_Loop -= 1

			Row["Alloy_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Strength_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Stop_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Drop_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Regular_Sets"] = {"Fixed": [], "Input": []}
			
			Row["Alloy_Weight"] = _Stat.Alloy_Weight - (_Stat.Alloy_Weight % 5) + 5



			# print(i.Template.Exercise_Type + " Set Scheme: ")			
# 			UNFILLED SETS GENERATED HERE
			if not StrengthStop and not StrengthDrop:
				Remaining_Sets = i.Template.Sets - Num_Filled_Sets
			else:				
				if StrengthStop:
					if i.Stopped or i.Maxed_Sets:
						Remaining_Sets = 0
					else:
						Remaining_Sets = 1	
				if StrengthDrop:
						Remaining_Sets = 1	

			for R in range(Remaining_Sets):
				Unfilled_Set_Dict = {}
				Unfilled_Set_Dict["Code"] = i.Template.Exercise_Type + "Set" + str(R)
				Unfilled_Set_Dict["Number"] = R + Num_Filled_Sets + 1
				Unfilled_Set_Dict["Index"] = R + Num_Filled_Sets

				Set_Row = [i.Template.Exercise_Type + "Set" + str(R), ""]
				Alloy_Row = [i.Template.Exercise_Type + "Alloy_Set", ""]
				Set_Number = R + Num_Filled_Sets + 1
				Set_Index = R + Num_Filled_Sets

				Set_Row.append(Set_Number)
				Alloy_Row.append(Set_Number)
				if Special_Sets:
					# Rep_List = i.Template.Special_Reps.split("-")
					# Reps = Rep_List[Set_Index]					
					# Unfilled_Set_Dict["Reps"] = Rep_List[Set_Index]					
					Unfilled_Set_Dict["Reps"] = Set_Rep_List[Set_Index]
				else:
					Reps = i.Template.Reps									
					Unfilled_Set_Dict["Reps"] = Row["Reps"]
				
				Unfilled_Set_Dict["Weight"] = i.Suggested_Weight
				Unfilled_Set_Dict["Stop"] = i.Template.Strength_Stop
				Unfilled_Set_Dict["Drop"] = i.Template.Strength_Drop



				Set_Row.append(Row["Reps"])
				Alloy_Row.append(Row["Reps"])

				Set_Row.append(i.Suggested_Weight) 
				Alloy_Row.append(i.Suggested_Weight)

# 				TIME-SORT FOR UNFILLED SETS
				if Future and False:
					Filled_Set = {}
					# Check what type of set it is here
					Filled_Set["Reps"] = i.Template.Reps
					Filled_Set["Weight"] = ""  
					Filled_Set["RPE"] = "" 
					Filled_Set["Tempo"] = "" 
					Set_Loop -= 1					
					if i.Alloy and Alloy_Sub and R == Remaining_Sets - 1:
							Row["Filled_Alloy"].append(Filled_Set)
					else:
						Row["Filled_Sets"].append(Filled_Set)
				elif Past and False:
					Filled_Set = {}
					# Check what type of set it is here
					Filled_Set["Reps"] = i.Template.Reps
					Filled_Set["Weight"] = "Old Set"  
					Filled_Set["RPE"] = "" 
					Filled_Set["Tempo"] = "" 
					Set_Loop -= 1					
					if i.Alloy and Alloy_Sub and R == Remaining_Sets - 1:
							Row["Filled_Alloy"].append(Filled_Set)
					else:
						Row["Filled_Sets"].append(Filled_Set)
#				ADDING UNFILLED SETS AS ROWS 
				elif i.Template.Drop_Set:
					Row["Strength_Sets"]["Input"].append(Unfilled_Set_Dict)					
					# Row["Strength_Sets"]["Input"].append(Set_Row)
				elif i.Template.Stop_Set:
					Row["Strength_Sets"]["Input"].append(Unfilled_Set_Dict)					
					# Row["Strength_Sets"]["Input"].append(Set_Row)
				elif i.Template.Alloy and Alloy_Sub:
					Alloys_Complete = False									
					if R == Remaining_Sets - 1:
						Unfilled_Set_Dict["Code"] = i.Template.Exercise_Type + "Alloy_Set"
						if i.Show_Alloy:
							Row["Alloy_Sets"]["Input"].append(Unfilled_Set_Dict)
							# print("Alloy Set (Input)")
							# Row["Alloy_Sets"]["Input"].append(Alloy_Row)
						else:
							Row["Alloy_Sets"]["Fixed"].append(Unfilled_Set_Dict)
							# Row["Alloy_Sets"]["Fixed"].append(Alloy_Row)
							# print("Alloy Set (Fixed)")
						continue
					else:
						Row["Regular_Sets"]["Input"].append(Unfilled_Set_Dict)					
						# Row["Regular_Sets"]["Input"].append(Set_Row)
						# print("Regular Set (Input)")
				else:
					Row["Regular_Sets"]["Input"].append(Unfilled_Set_Dict)					
					# Row["Regular_Sets"]["Input"].append(Set_Row)
					# print("Regular Set (Input)")
			
			Last_Set_Index = i.Template.Sets - 1
			# if StrengthStop or StrengthDrop:
			# 	Empty_Sets = 0
			# 	# Empty_Sets = 4 - Num_Filled_Sets - 1
			# else:
			# 	Empty_Sets = 4 - i.Template.Sets

			Empty_Sets = 4 - i.Template.Sets

			if Empty_Sets > 0:
				for n in range(Empty_Sets):
					Row["Empty_Sets"].append("Empty_Set")

			context["Patterns"].append(Row)

# 			ON GET ALLOY PRESS, IDENTIFY WHICH EXERCISE
			if request.GET.get(i.Template.Exercise_Type + "_Get_Alloy"):
				print("Getting Alloy Set for: " + i.Template.Exercise_Type)
				i.Show_Alloy = True
				i.save()
				Get_Alloy_Pressed = True
				request.session["Show_Alloy_Type"] = i.Template.Exercise_Type
				# _Stat.Alloy_Weight = Get_Weight(_Stat.Max, _Reps_Estimate + 1, 10) 
				# return HttpResponseRedirect("/userpage")

			if request.GET.get(i.Template.Exercise_Type + "_Get_Set"):
				print("Getting SS Set for: " + i.Template.Exercise_Type)
				Get_Set_SS = True
				request.session["SS_Type"] = i.Template.Exercise_Type

			if request.GET.get(i.Template.Exercise_Type + "_Get_Drop"):
				print("Getting SD Set for: " + i.Template.Exercise_Type)
				Get_Set_SD = True
				request.session["SD_Type"] = i.Template.Exercise_Type
				# return HttpResponseRedirect("/userpage")

#		CHECK IF ALLOYS HAVE BEEN COMPLETED (Show "Submit Workout" button) 
		if Alloys_Complete:
			context["Alloys_Complete"] = ["Yes"]
		else:
			context["Alloys_Complete"] = []

# 		CHECK IF THE WORKOUT DAY HAS SUBWORKOUTS AT ALL... (?)
		if len(_Workout.SubWorkouts.all()) > 0:
			context["Workout_Day"][0].append("True")
		else:
			context["Workout_Day"][1].append("False")

# 		FORM SUBMIT-CHECK STARTS HERE
		if request.GET.get("Submit_Workout") or Get_Alloy_Pressed or Get_Set_SS or Get_Set_SD:
			# print(request.GET.keys())
# 			LOOPING THROUGH SETS
			for _Sub in _Workout.SubWorkouts.all():
				Set_Stats = ""
				Alloy_Sub = False
				if Alloy_Workout and _Sub.Money != 0 and _Sub.Money != None:
					Alloy_Sub = True

				_E_Type = _Sub.Template.Exercise_Type
				_E_Name = _Sub.Exercise.Name

				_Stat, Created = Stat.objects.get_or_create(Type=_E_Type, Member=_Member)

				if _Sub.Template.Strength_Stop != 0:
					Unfilled_Sets_Shown = 1
				elif _Sub.Template.Strength_Drop != 0:
					Unfilled_Sets_Shown = 1
				else:
					Unfilled_Sets_Shown = _Sub.Template.Sets - _Sub.Filled_Sets

				if Alloy_Sub:
					Unfilled_Sets_Shown -= 1
				if _Sub.Maxed_Sets or _Sub.Stopped:
					Unfilled_Sets_Shown = 0

#				REGULAR UNFILLED SETS HANDLED HERE (NON-ALLOY)
				for n in range(Unfilled_Sets_Shown):
					if _Sub.Template.Special_Reps == "":
						_Reps = str(_Sub.Template.Reps)
					else:
						_Reps = _Sub.Template.Special_Reps.split(",")[n]

					_Weight = ""
					_RPE = "10"
					_Tempo = ""

					Prefix = _E_Type + "Set" + str(n)

					Rep_Code = Prefix + "_Reps"
					Weight_Code = Prefix + "_Weight"
					RPE_Code = Prefix + "_RPE" 

					Tempo_Code_1 = Prefix + "_Tempo_1"
					Tempo_Code_2 = Prefix + "_Tempo_2"
					Tempo_Code_3 = Prefix + "_Tempo_3"

					Set_Label = "B" + str(n + 1)

					Filled = True


					if _Sub.Special_Sets:
						_Reps = _Sub.Template.Reps.split("-")[n + _Sub.Filled_Sets]
					elif Rep_Code in request.GET.keys():
						_Reps = request.GET[Rep_Code]
						if _Reps == "":
							Filled = False
					if Weight_Code in request.GET.keys():
						_Weight = request.GET[Weight_Code]
						if _Weight == "":
							Filled = False
					if RPE_Code in request.GET.keys():
						_RPE = request.GET[RPE_Code]
						if _RPE == "":
							Filled = False
					if Tempo_Code_1 in request.GET.keys():
						Tempo_1 = request.GET[Tempo_Code_1] 
						Tempo_2 = request.GET[Tempo_Code_2] 
						Tempo_3 = request.GET[Tempo_Code_3] 
						_Tempo = Tempo_1 + "-" + Tempo_2 + "-" + Tempo_3
						if Tempo_1 == "" or Tempo_2 == "" or Tempo_3 == "":
							Filled = False

					if Filled:
						if Alloy_Sub:
							Set_Label = "A" + str(n + 1)
						else:
							Set_Label = "R" + str(n + 1)

					Stats = Set_Label + "," + _Reps + "," + _Weight + "," + _RPE + "," + _Tempo + "/"
					Set_Stats += Stats

				Set_List = Set_Stats.split("/")
				print("Set_List: " + str(Set_List))
				Set_List.remove('')

#				ADDING FILLED SETS TO SUBWORKOUT SET STRING 
				if _Sub.Filled_Sets < 6:
					_Sub.Set_Stats += "/" + "/".join(Set_List)
					_Sub.Maxed_Sets = False
					_Sub.save()
				else:
					_Sub.Maxed_Sets = True
					_Sub.save()

				Last_Set = ["", "", "", "", ""]
				if len(Set_List) >= 1: 
					Last_Set = Set_List[-1].split(",")

					# 	if Last_Set[3] =="X" or Last_Set[3] == "10":
					# 		Sub.Sets += 1
					# 	else:

						# return HttpResponseRedirect("/userpage")
				if Get_Set_SS and request.session["SS_Type"] == _Sub.Template.Exercise_Type and False:	
					print("Last Set: " + str(Last_Set))
					print("Checking Strength Stop")				
					print("Last Set 3: " + str(Last_Set[3]))
					print(_Sub.Template.Strength_Stop)
					if _Sub.Maxed_Sets:
						return HttpResponseRedirect("/userpage")
					if Last_Set[3] != "" and float(Last_Set[3]) >= _Sub.Template.Strength_Stop:
						print("Strength Stop Matched!!")
						_Sub.Stopped = True
						_Sub.save()
						return HttpResponseRedirect("/userpage")
					else:
						_Sub.Stopped = False
						_Sub.save()
						print("Strength Stop Not Matched!!")
						return HttpResponseRedirect("/userpage")
 
				# if Get_Set_SD and request.session["SD_Type"] == _Sub.Template.Exercise_Type:		
				if Get_Set_SS and request.session["SS_Type"] == _Sub.Template.Exercise_Type:	
					print("Line 826")
					# return HttpResponseRedirect("/userpage")
					if _Sub.Maxed_Sets:
						return HttpResponseRedirect("/userpage")
					else:
						if Last_Set[3] != "" and (float(Last_Set[3]) >= 10 or Last_Set[3] == "X"):
							if not _Sub.Dropped:
								_Sub.Suggested_Weight = _Sub.Suggested_Weight*(100 - 10)
								_Sub.Drop_Sets += 1
								_Sub.Dropped = True
								_Sub.Stopped = False
								_Sub.save()
							elif _Sub.Dropped:
								_Sub.Stopped = True
								_Sub.save()
							return HttpResponseRedirect("/userpage")
						else:
							_Sub.Dropped = False
							_Sub.save()
							return HttpResponseRedirect("/userpage")
					return HttpResponseRedirect("/userpage")
					# Update Stat Max Here
					# _Stat.Max = 
				elif not BodyWeight:
					_Reps_Estimate = int(_Reps)
					_Weight_Estimate = _Stat.Max
					# _RPE_Estimate = int(_Sub.RPE)
					_RPE_Estimate = 10

# 				GETTING VALUES TO ESTIMATE NEW MAX
					if Last_Set[2] != "":
						_Weight_Estimate = int(Last_Set[2])
					if Last_Set[1] != "":
						_Reps_Estimate = int(Last_Set[1])
					if Last_Set[3] != "":
						if Last_Set[3] == "X":
							_RPE_Estimate = 10
							_Weight_Estimate = _Weight_Estimate*0.75
						else:
							_RPE_Estimate = float(Last_Set[3])
					if _RPE_Estimate > 10:
						_RPE_Estimate = 10

# 				ESTIMATING NEW MAX FOR SET
					_Stat.Max = Get_Max(_Weight_Estimate, _Reps_Estimate, _RPE_Estimate)
					_Stat.save()


# 				SHOW ALLOY SET + GETTING ALLOY WEIGHT
				if Get_Alloy_Pressed and request.session["Show_Alloy_Type"] == _Sub.Template.Exercise_Type:
					_Stat.Alloy_Weight = Get_Weight(_Stat.Max, _Sub.Template.Money + 1, 10)
					_Stat.save()
					print("New Alloy Weight: " + str(_Stat.Alloy_Weight))
# 				ALLOY SET SUBMISSIONS HANDLED HERE
				elif request.GET.get("Submit_Workout") or (Get_Alloy_Pressed 
				and request.session["Show_Alloy_Type"] != _Sub.Template.Exercise_Type):
					# print("Line 803 Executing")
					if Alloy_Sub and _Sub.Show_Alloy:
						_Rep_Code = _Sub.Template.Exercise_Type + "Alloy_Set_Reps"
						if _Rep_Code in request.GET.keys() and request.GET[_Rep_Code] != "":
							_Tempo_1_Code = _Sub.Template.Exercise_Type + "Alloy_Set_Tempo_1"
							_Tempo_2_Code = _Sub.Template.Exercise_Type + "Alloy_Set_Tempo_2"
							_Tempo_3_Code = _Sub.Template.Exercise_Type + "Alloy_Set_Tempo_3"
							Tempo = ""
							if _Tempo_1_Code in request.GET.keys():
								_Tempo_1 = request.GET[_Tempo_1_Code]
								_Tempo_2 = request.GET[_Tempo_2_Code]
								_Tempo_3 = request.GET[_Tempo_3_Code]
								Tempo = _Tempo_1 + "-" + _Tempo_2 + "-" + _Tempo_3
							print("Checking Alloy")
							Performed_Reps = request.GET[_Rep_Code]
							_Weight = _Stat.Alloy_Weight

							print("ALLOY SET STATS: ")
							print("	REPS: " + str(Performed_Reps))
							print("	WEIGHT: " + str(_Stat.Alloy_Weight))
							print("	TEMPO: " + str(Tempo))
							print(" VS REQUIREMENT: " + str(_Stat.Alloy_Reps))
# 	CHECK IF PASSED ALLOY SET HERE
							if int(Performed_Reps) >= _Stat.Alloy_Reps:
								_Stat.Level_Up = True
								_Stat.Failed = False
								_Stat.save()
								_Sub.Alloy_Passed = True
								_Sub.save()
							elif int(Performed_Reps) < _Stat.Alloy_Reps:
								_Stat.Level_Up = False
								_Stat.Failed = True
								_Stat.save()
								_Sub.Alloy_Passed = False
								_Sub.save()
# 	ADD TO SUBWORKOUT SET STATS STRING
							Set_Label = "A" + str(_Sub.Sets)
							Stat_String = Set_Label + "," + str(Performed_Reps) + "," + str(_Weight) + ",10," + Tempo
							Stat_List = Stat_String.split("/")
							# Stat_List.remove('')
							_Sub.Set_Stats += "/" + Stat_String
							_Sub.save()
#				WORKOUT SUBMITTED 
				if request.GET.get("Submit_Workout"):
					_Workout.Submitted = True
					_Workout.save()
					# _Workout.Completed = True
					# _Workout.save()
#				LAST WORKOUT/LEVEL-UP CHECK 
					if _Workout.Template.Last:					
						request.session["Level_Up"] = Check_Level_Up(_Member)			
						_Member.Has_Workout = False		
						# if Check_Level_Up(_Member):
						return HttpResponseRedirect("/level-up")

			_Workout.Submitted = True
			_Workout.save()			
			return HttpResponseRedirect("/userpage")


		print(str(Workout_Date.strftime("%y/%m/%d")))
		print(str(datetime.now().strftime("%y/%m/%d")))			

# 	VIDEO-BUTTON CHECK HERE 
	if request.GET.get("Video"):
		print("Video PK: " + request.GET["Video"])
		_PK = int(request.GET["Video"])
		request.session["Video_PK"] = _PK
		return HttpResponseRedirect("/videos")

# 	RESET-BUTTON CHECK  HERE 
	if request.GET.get("clear_all"):
		_Workout.Completed = False
		_Workout.save()
		for i in _Workout.SubWorkouts.all():
			Reset_Sets = []
			for n in range(i.Template.Sets):				
				Reset_Sets.append("B" + str(n + 1) + ",,,,")
			i.Set_Stats = "/".join(Reset_Sets)
			# i.Set_Stats = "/".join(Filled_Sets)
			i.Show_Alloy = False
			i.Maxed_Sets = False
			i.Stopped = False
			i.Dropped = False
			i.save()
		return HttpResponseRedirect("/userpage")

# 	CALENDAR STUFF HERE
	for workout_date in workout_date_list:
		parsed_date_list = workout_date.split('/')
		parsed_date_dict = {}
		if (len(parsed_date_list) == 3): 
			parsed_date_dict[str('month')] = str(parsed_date_list[0])
			parsed_date_dict[str('day')] = str(parsed_date_list[1])
			parsed_date_dict[str('year')] = str(parsed_date_list[2])
			final_list.append(parsed_date_dict)

	context['final_list'] = json.dumps(final_list)
	context["Date"] = _Date

	if request.method == "POST":
		print("905 Redirecting")
		return HttpResponseRedirect("/userpage")

	return render(request, "userpage.html", context)

@csrf_exempt 
def Workout_Update(request): 
	context = {}
	context["Date"] = ""
	_User = request.user
	_Member = Member.objects.get(User = _User)
	if request.method == 'POST': 
		if 'TempDate' in request.POST: 
			# test_var = date 
			context["Date"] = request.POST["TempDate"]
			request.session["Calendar_Date"] = request.POST["TempDate"]
			test_var = request.POST['TempDate']
			# print "Request is", request 
			# print test_var
			# print isinstance(test_var, basestring)
			workoutDict = {}
			# need to filter on user id here
			workout_list = Workout.objects.filter(_Date=test_var, Member=_Member)
			counter = 0 
			# for workout in workout_list: 
			# 	counter +=1 
			# 	subworkout_list = workout.SubWorkouts.all()
			# 	subworkout_counter = 0 
				 
			# 	for subworkout in subworkout_list: 
			# 		subworkoutDict = {
			# 			'level': str(workout.Level), # for now, extract levels for each subworkout
			# 			'exercise_type': subworkout.Exercise_Type,
			# 			'exercise_name': subworkout.Exercise.Name,
			# 			'sets': str(subworkout.Sets),
			# 			'reps': str(subworkout.Reps),
			# 			'rpe': str(subworkout.RPE),
			# 			'date': workout._Date
			# 		}
			# 		workoutDict[subworkout_counter] = subworkoutDict
			# 		subworkout_counter += 1
			# print workoutDict	
			return HttpResponseRedirect("/userpage")
			# return JsonResponse(workoutDict)
		else: 
			return HttpResponseRedirect("/userpage")

@csrf_exempt 
def RPE_Update(request): 
	if request.method == 'POST': 
		current_date = request.POST['current_date']
		# need to filter on user id here
		workout_list = Workout.objects.filter(_Date=current_date);

		for workout in workout_list: 
				subworkout_list = workout.SubWorkouts.all()
				subworkout_counter = 0 
				 
				for subworkout in subworkout_list: 
					if (subworkout_counter == 0): 
						subworkout.RPE = request.POST['RPE_row1']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 1): 
						subworkout.RPE = request.POST['RPE_row2']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 2): 
						subworkout.RPE = request.POST['RPE_row3']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 3): 
						subworkout.RPE = request.POST['RPE_row4']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 4): 
						subworkout.RPE = request.POST['RPE_row5']
						subworkout.save()
						workout.save()					
					# subworkoutDict = {
					# 	'level': str(workout.Level),
					# 	'exercise_type': subworkout.Exercise_Type,
					# 	'exercise_name': subworkout.Exercise.Name,
					# 	'sets': str(subworkout.Sets),
					# 	'reps': str(subworkout.Reps),
					# 	'date': workout._Date
					# }
					# workoutDict[subworkout_counter] = subworkoutDict
					subworkout_counter += 1

		return HttpResponse('success'); 



@user_passes_test(User_Check, login_url="/")
def Past_Workouts(request):
	context = {}
	_User = request.user
	_Member = Member.objects.get(User=_User)
	Workouts = _Member.workouts.all()
	
	context["Workout_Info"] = []
	context["Selected_Workout"]  = []
	context["Workout_Date"] = [[], []]

	if "Selected_Date" in request.session.keys():
		_Date = request.session["Selected_Date"]
		context["Workout_Date"] = [_Date]
		_Workout = Workout.objects.get(_Date = _Date, Member = _Member)
		context["Workout_Level"] = _Workout.Level
		for n in _Workout.SubWorkouts.all():
			Sub = []
			Sub.append(n.Exercise_Type)
			Sub.append(n.Exercise.Name)
			Sub.append(n.Sets)
			Stats = n.Set_Stats.split("/")
			Stat_List = [[], []]
			for string in Stats:
				if n.Alloy and string == Stats[-1]:
					# Set_List = string.split(",")
					Set_List = "145,Alloy,8".split(",")
					Stat_List[1].append(Set_List)
				else:
					Set_List = "145,8,8".split(",")
					# Set_List = string.split(",")
					Stat_List[0].append(Set_List)
			Sub.append(Stat_List)
			context["Selected_Workout"].append(Sub)
			Sub.append(n.Set_Stats)
	for i in Workouts:
		row = []
		row.append(i._Date)
		row.append(i.Level)
		row.append(i.Template.Week)
		row.append(i.Template.Day)
		if i.Alloy:
			row.append("Alloy")
		else:
			row.append("Regular")
		context["Workout_Info"].append(row)

	if request.method == "POST":
		print(request.POST["Submitted_Date"])
		request.session["Selected_Date"] = request.POST["Submitted_Date"]
		return HttpResponseRedirect("/past-workouts")
	return render(request, "pastworkouts.html", context)

Days_Of_Week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

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

	if "Level_Up" not in request.session.keys():
		request.session["Level_Up"] = True

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
