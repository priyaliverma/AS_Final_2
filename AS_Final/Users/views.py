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
from Shared_Functions import *
from Pause_Tempo import Pause_Dict, Tempo_Dict, UBV_Pull_Tempo


Exercise_Types = ["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat", "LB Uni Push", 
"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2", "Carry", "Medicine Ball"]

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

# RPEs = ["X (Failure)", "1-2", "3-4", "5-6", "7", "8", "8.5", "9", "9.5", "10"]

RPEs = [["1-2", 1], ["3-4", 3], ["5-6", 5], ["7", 7], ["8", 8], ["8.5", 8.5], ["9", 9], ["9.5", 9.5], ["10", 10]]
RPEs.reverse()

@user_passes_test(Member_Exists, login_url="/")
@user_passes_test(Member_Paid, login_url="/sign-up-confirmation")
@user_passes_test(Member_Agreed, login_url="/waiver")
@user_passes_test(Member_Read, login_url="/terms-conditions")
@user_passes_test(Member_Has_Workouts, login_url="/welcome")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
def User_Page(request): 
	_User = request.user
	_Member = Member.objects.get(User = _User)
	Workouts = Workout.objects
	workout_date_list = Workouts.filter(Member=_Member, Current_Block=True, Completed=False).values_list('_Date', flat=True).distinct()
	context = {}
	final_list = []
	context["Level"] = _Member.Level

	context["Patterns"] = []
	context["Workout_Stats"] = []

	context["Alloy"] = ""

	context["First_Name"] = _User.first_name 

	context["Has_Workouts"] = _Member.Has_Workouts

	if _Member.Has_Workouts and _Member.Finished_Workouts:
		context["Finished_Workouts"] = True

	Uncompleted_Workouts = Workouts.filter(Member=_Member, Completed=False)
	Upcoming_Workouts = []
	for U in Uncompleted_Workouts:
		_Date = datetime.strptime(U._Date, "%m/%d/%Y")
		if _Date.date() >= datetime.now().date():
			Delta = _Date.date() - datetime.now().date()
			print("Future Uncompleted Workout Workout " + str(Delta) + " Days ahead")
			Upcoming_Workouts.append(U)
		elif _Date.date() < datetime.now().date():
			print("Past Uncompleted Workout Workout")
			U.Completed = True
			U.save()
	
	print("Number of remaining workouts: " + str(len(Upcoming_Workouts)))

	if len(Upcoming_Workouts) == 0:
		_Member.Finished_Workouts = True
		_Member.save()
	print("Finished Workouts: " + str(_Member.Finished_Workouts))
	# _Member.Finished_Workouts = False
	# _Member.save()

	# Reversed_RPE = reversed(RPEs)
	# RPEs.reverse()
	context["RPE_List"] = RPEs

	_Date = datetime.now().strftime("%m/%d/%Y")
	_Stats = _Member.Stats.all()

	for _stat in _Stats:
		print(_stat.Type + " " + str(_stat.Max))

	if "Calendar_Date" in request.session.keys():
		print(request.session["Calendar_Date"])
		_Date = request.session["Calendar_Date"]
	else:
		request.session["Calendar_Date"] = datetime.now().strftime("%m/%d/%Y")

	Workout_Day = False
	Alloy_Workout = False
	Show_Alloy = False

	Requires_Tempo = False
	Alloys_Complete = True

	if _Date == datetime.now().strftime("%m/%d/%Y") and Workout.objects.filter(_Date=_Date, Member=_Member, Completed=True).exists():
		context["Workout_Completed_Same_Day"] = True

	if Workout.objects.filter(_Date=_Date, Member=_Member, Completed=False).exists():
		if Workout.objects.filter(_Date=_Date, Member=_Member, Completed=False).count() > 1:
			Workout.objects.filter(_Date=_Date, Member=_Member, Completed=False)[0].delete()

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
		context["Workout_Day"] = False

	Show_Alloy = False

# 	WORKOUT DAY STUFF STARTS HERE
	if Workout_Day:
		context["Workout_Day"] = True

		_Workout = Workout.objects.get(_Date=_Date, Member=_Member, Completed=False)

		context["Workout_Stats"].append(_Workout.Level)
		context["Workout_Stats"].append(_Workout.Template.Week)
		context["Workout_Stats"].append(_Workout.Template.Day)

		context["Tempo_Required"] = False
		context["Tempo"] = []

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
			# context["Workout_Day_Time"][1].append("True")
			context["Workout_Day_Time"] = "Same"
			Same_Day = True
		elif Workout_Date < datetime.now():
			# context["Workout_Day_Time"][0].append("True")
			context["Workout_Day_Time"] = "Past"
			Past = True
			print("PAST IS TRUE")
			context["Past"] = "This workout has now expired. Please view your results in your Profile Page"
		elif Workout_Date > datetime.now():
			context["Future"] = "It is not time to complete this workout yet. Please come back to this date later."
			context["Workout_Day_Time"] = "Future"
			Future = True
		if _Workout.Template.Last:	
			print("Last workout detected")

# 		FOR TESTING:
		context["Workout_Day_Time"] = "Same"
		# _Workout.Completed = False
		# _Workout.save()
		# Same_Day = True
		# Past = False
		# Future = False

# 		SUB-WORKOUT LOOP # 1
		for i in _Workout.SubWorkouts.all():
			Special_Sets = False
			StrengthStop = False
			StrengthDrop = False
			Suggested_Weight = i.Suggested_Weight
			Tempo_Required = _Workout.Template.Has_Tempo

			Template = i.Template
			
			Tempo = False
			Bodyweight = False
			Special_Sets = False
			Carry = False
			Alloy_Sub = False
			Alloy_Reps = 0

			Row = {}
			Row["Reps"] = i.Template.Reps

			Row["Set_Stats"] = i.Set_Stats

			Row["Sets_Reps"] = str(i.Template.Sets) + " x " + str(i.Template.Reps) + " @ " + str(i.Template.RPE) + " RPE"

			Row["Has_Tempo"] = False
			Row["Is_Bodyweight"] = False
			Row["Carry_Workout"] = False
			Row["Is_Alloy_Sub"] = False
			Row["Alloy_Final"] = False
			Row["Is_SS"] = False
			Row["Is_SD"] = False
			Row["Dropped"] = False

			Effective_Level = i.Exercise.Level
			if "Pause" in i.Exercise.Name: 
				if Effective_Level >= 21:
					Row["Pause_String"] = Pause_Dict[5]
				elif Effective_Level >= 16:
					Row["Pause_String"] = Pause_Dict[4]
				elif Effective_Level >= 11:
					Row["Pause_String"] = Pause_Dict[3]
				elif Effective_Level >= 6:
					Row["Pause_String"] = Pause_Dict[2]
				elif Effective_Level >= 0:
					Row["Pause_String"] = Pause_Dict[1]
			if "Tempo" in i.Exercise.Name:
				if Effective_Level >= 21:
					Row["Tempo_String"] = Tempo_Dict[5]
				elif Effective_Level >= 16:
					Row["Tempo_String"] = Tempo_Dict[4]
				elif Effective_Level >= 11:
					Row["Tempo_String"] = Tempo_Dict[3]
				elif Effective_Level >= 6:
					Row["Tempo_String"] = Tempo_Dict[2]
				elif Effective_Level >= 0:
					Row["Tempo_String"] = Tempo_Dict[1]
				# Row["Pause_String"] = 
			elif i.Exercise.Type == "UB Vert Pull" and i.Exercise.Level in UBV_Pull_Tempo.keys():
				Row["Tempo_String"] = UBV_Pull_Tempo[i.Exercise.Level]

			if "Tempo" in i.Exercise.Name:
				Tempo = True
				Tempo_Required = True
				Row["Tempo_Required"] = True
				context["Tempo_Required"] = True
				Sub_Tempo = True
			else:
				Row["Tempo_Required"] = False
				Sub_Tempo = False
			Row["Tempo_Required"] = False
			context["Tempo_Required"] = True

			# Row["Tempo"] = ["Y"]

			if i.Template.Deload != 0 and i.Template.Deload != None:
				Row["Deload"] = str(i.Template.Deload) + " (Level " + str(_Member.Level + i.Template.Deload) + ")"
				Row["Level"] = "Level " + str(_Member.Level + i.Template.Deload)
			else:
				Row["Deload"] = "None"
				Row["Level"] = "Level " + str(_Member.Level)


			if Template.Reps == "" or Template.Reps == "0" or Template.Reps == "B":
				Row["Suggested_Weight"] = "Bodyweight"
				Row["Sets_Reps"] = str(i.Template.Sets) + " Sets " + " @ " + str(i.Template.RPE) + " RPE"
				Row["Reps"] = "Bodyweight"
				Row["BodyWeight"] = True
				Bodyweight = True
			else:
				Row["Suggested_Weight"] = "Weight: None"
				Bodyweight = False
				Row["BodyWeight"] = False

			Set_Rep_List = []

			if re.search("-", i.Template.Reps) != None:
				Special_Sets = True
				i.Special_Sets = True
				i.save()
				Rep_String = i.Template.Reps.replace("-", ", ")
				Set_Rep_List = i.Template.Reps.split("-")				
				Row["Reps"] = Rep_String
				Row["Sets_Reps"] = str(i.Template.Sets) + " Sets (" + Rep_String + ") @ " + str(i.Template.RPE) + " RPE"

			if Template.Exercise_Type == "Carry":
				Carry = True
				Row["Reps"] = str(Row["Reps"]) + " (s)"
			# Row["SS_Btn"] = False
			if Template.Strength_Stop > 0:
				StrengthStop = True
				Row["Pre_SR"] = ["Alloy Stop: " + str(i.Template.Strength_Stop)]
				Row["Sets_Reps"] =  str(i.Template.Reps) + " @ " + str(i.Template.RPE) + " RPE"
				Row["Additional_Info"] = "Alloy Stop"
				if not i.Stopped and not i.Maxed_Sets and i.Template.Strength_Stop != 0:
					Row["SS_Btn"] = True
					Row["Strength_Stop"] = [i.Template.Strength_Stop]
					Row["Strength_Drop"] = []
			elif Template.Strength_Drop > 0:
				Row["Pre_SR"] = ["Strength Drop: " + str(i.Template.Strength_Drop) + "%"]
				Row["Sets_Reps"] = str(i.Template.Reps) + " @ " + str(i.Template.RPE) + " RPE"
				StrengthDrop = True
				if not i.Stopped and not i.Maxed_Sets and i.Template.Strength_Drop != 0:
					Row["SD_Btn"] = True
					Row["Strength_Stop"] = []
					Row["Strength_Drop"] = [i.Template.Strength_Drop]
			else:
				Row["SS_Btn"] = False
				Row["SD_Btn"] = False
				Row["Strength_Stop"] = []
				Row["Strength_Drop"] = []

			if i.Maxed_Sets or i.Stopped:
				Row["SS_Btn"] = False
				Row["SD_Btn"] = False
				Row["Strength_Stop"] = []
				Row["Strength_Drop"] = []

			if _Workout.Template.Alloy and i.Template.Alloy_Reps != 0 and i.Template.Alloy_Reps != None:
				Template.Alloy = True
				Alloy_Sub = True
				Alloy_Reps = Template.Alloy_Reps
			_Stat, Created = Stat.objects.get_or_create(Type=i.Template.Exercise_Type, Member=_Member)		
			_Stat = Stat.objects.get(Type = i.Template.Exercise_Type, Member=_Member)				
			# GENERAL INFORMATION HERE WEIGHTS FOR FIRST COLUMN
			Row["Money"] = i.Template.Alloy_Reps
			Row["Exercise_Type"] = i.Template.Exercise_Type
			Row["Exercise_Name"] = i.Exercise.Name
			Row["Sets"] = i.Template.Sets
			Row["RPE"] = i.Template.RPE

			if (len(i.Exercise.Video.all()) > 0):
				Row["Has_Video"] = True
				_Video = i.Exercise.Video.all()[0]
				Row["Video_PK"] = _Video.pk

			Reps = i.Template.Reps

# 			DETERMINING WEIGHT HERE
			Weight_String = ""
			No_Max = False
			if _Stat.Max != 0 and i.Template.Reps != "" and i.Template.Reps != "B":
				if len(i.Template.RPE) == 1:
					_RPE = int(i.Template.RPE)
				elif re.search("-", i.Template.RPE) != None:
					_RPE = int(i.Template.RPE.split("-")[0])
				else:
					_RPE = 10
				if i.Template.Reps != "B":
					if Special_Sets:
						Estimate = Get_Weight(_Stat.Max, int(Set_Rep_List[1]), _RPE)						
					else:
						Estimate = Get_Weight(_Stat.Max, int(i.Template.Reps), _RPE)			
				Weight_Origin = str(_Stat.Max) + " lbs " + str(i.Template.Reps) + " " + str(_RPE)
				Range_Min = Estimate - (Estimate % 5)
				Range_Max = Range_Min + 5
				i.Suggested_Weight = Range_Min
				if StrengthDrop:
					i.Drop_Weight = Range_Min*(100 - i.Template.Strength_Drop)/100
				i.save()


				if StrengthDrop and not StrengthStop: 
					i.Suggested_Weight = Range_Min
					i.save()
				# # FOR TESTING
				# if StrengthStop and i.Dropped:
				# 	i.Suggested_Weight = Range_Min*(0.93)
				# 	i.save()
				# REAL
				# if StrengthDrop and i.Dropped:
				# 	print("Line 579 (DROP DETECTED)")
				# 	print(i.Template.Strength_Drop)
					# i.Suggested_Weight = Range_Min
					# i.Suggested_Weight = Range_Min*(100 - i.Template.Strength_Drop)/100
					# i.save()
				Weight_String = str(Range_Min) + "-" + str(Range_Max) + " lbs" 
				Row["Suggested_Weight"] = "Weight: " + Weight_String
				Row["Estimated_Max"] =  Weight_Origin
			elif _Stat.Max == 0 and not Bodyweight:
				No_Max = True
			Row["Alloy_Weight"] = i.Alloy_Weight - (i.Alloy_Weight % 5) + 5
			# Row["Alloy_Weight"] = str(i.Alloy_Weight) + " " + i.Template.Exercise_Type 

			Row["Alloy_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Strength_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Stop_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Drop_Sets"] = {"Filled": [], "Input": [], "Completed": []}
			Row["Regular_Sets"] = {"Fixed": [], "Input": []}			
			Row["Empty_Sets"] = []
			Row["Filled_Sets"] = []
			Row["Filled_Alloy"] = []

			Row["All_Unfilled"] = []
			Row["All_Filled_Sets"] = []

			Row["Input_ID"] = i.Template.Exercise_Type

			Set_List = i.Set_Stats.split("/")
			Num_Filled_Sets = 0
			Filled_Sets = []

# 			FILLED SETS CREATED HERE
			#CHECK FOR NUMBER OF UNFILLED SETS
			if "" in Set_List:
				Set_List.remove("")
			for Set in Set_List:
				if Set != "":
					if Set[0][0] == "R" or  Set[0][0] == "A":
						Filled_Sets.append(Set)
					elif Set[0][0] == "B":
						First_Empty_Set_Num = Set.split(",")[0][1]
						Num_Filled_Sets = int(First_Empty_Set_Num) - 1
						break 
			Filled_Set_String = "/".join(Filled_Sets)
			#RE-ORGANIZE SET_STATS
			i.Set_Stats = ""
			i.Filled_Sets = len(Filled_Sets)			
			if i.Filled_Sets >= 6:
				i.Maxed_Sets = True
				i.save()
				Row["SS_Btn"] = False
				Row["SD_Btn"] = False


			#ADD FILLED SETS TO SET_STATS			
			i.Set_Stats = "/".join(Filled_Sets)
			i.save()
			#IMPORTANT: NUMBER OF FILLED SETS TO BE USED LATER			
			Num_Filled_Sets = len(Filled_Sets)
# 			FILLED SETS GET ADDED TO CONTEXT
			for n in range(Num_Filled_Sets):
				Set_Info = Set_List[n].split(",")
				if Set_Info != "" and len(Set_Info) >= 5:
					Filled_Set = {}
					Filled_Set["Reps"] = Set_Info[1]
					Filled_Set["Weight"] = Set_Info[2]
					if Bodyweight: 
						Filled_Set["Type"] = "Bodyweight"
						Filled_Set["Weight"] = "Bodyweight"
					elif Set_Info[2] == "":
						Filled_Set["Weight"] = i.Suggested_Weight
					Filled_Set["RPE"] = Set_Info[3]
					Filled_Set["Tempo"] = Set_Info[4] 
					if i.Dropped:
						Filled_Set["Type"] = "Dropped"
						Filled_Set["Drop_Weight"] = i.Drop_Weight
						Row["Drop_Sets"]["Filled"].append(Filled_Set)

					if Set_Info[0] == "A" + str(i.Template.Sets):
						Filled_Set["Type"] = "Alloy"
						Filled_Set["Reps"] = Set_Info[1]
						if i.Alloy_Passed:
							Filled_Set["Alloy_Passed_Bool"] = True
							Filled_Set["Alloy_Passed"] = "(Passed)"
						else:
							Filled_Set["Alloy_Passed_Bool"] = False
							Filled_Set["Alloy_Failed"] = "(Failed)"
						Row["Filled_Alloy"].append(Filled_Set)
					else:
						Row["Filled_Sets"].append(Filled_Set)

				Row["All_Filled_Sets"].append(Filled_Set)

# 			GETTING NUMBER OF UNFILLED INPUTS
			if i.Maxed_Sets or i.Stopped:
				Remaining_Sets = 0
			elif StrengthStop or StrengthDrop:
				Remaining_Sets = 1	
			else:
				Remaining_Sets = i.Template.Sets - Num_Filled_Sets

# 			UNFILLED SETS GENERATED HERE
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
				Unfilled_Set_Dict["Drop_Weight"] = i.Drop_Weight
				Unfilled_Set_Dict["Stop"] = i.Template.Strength_Stop
				Unfilled_Set_Dict["Drop"] = i.Template.Strength_Drop

				if No_Max:
					Unfilled_Set_Dict["Has_Weight"] = False
					Unfilled_Set_Dict["Yes_Weight"] = []
					Unfilled_Set_Dict["No_Weight"] = ["True"]
				else:
					Unfilled_Set_Dict["Has_Weight"] = True
					Unfilled_Set_Dict["Yes_Weight"] = ["True"]
					Unfilled_Set_Dict["No_Weight"] = []

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
					if i.Alloy and Alloy_Sub and R == Remaining_Sets - 1:
							Row["Filled_Alloy"].append(Filled_Set)
					else:
						Row["Filled_Sets"].append(Filled_Set)
#				ADDING UNFILLED SETS AS ROWS 
				elif i.Template.Drop_Set or i.Template.Strength_Drop > 0:
					print("Drop SET!!")
					if i.Dropped:
						print("Dropped")
						Row["Set_Type"] = "Dropped_Set"
					else:
						Row["Set_Type"] = "Strength_Input"
					# Row["Strength_Sets"]["Input"].append(Set_Row)
				elif i.Template.Stop_Set:
					Row["Set_Type"] = "Strength_Input"
					# Row["Strength_Sets"]["Input"].append(Set_Row)
				elif i.Template.Alloy and Alloy_Sub:
					Alloys_Complete = False									
					if R == Remaining_Sets - 1:
						# _Rep_Code = _Sub.Template.Exercise_Type + "Alloy_Set_Reps"
						Unfilled_Set_Dict["Money"] = i.Template.Alloy_Reps
						Row["Alloy_Sub"] = True
						Row["Alloy_Code"] = i.Template.Exercise_Type + "Alloy_Set"
						Unfilled_Set_Dict["Code"] = i.Template.Exercise_Type + "Alloy_Set"
						if i.Show_Alloy:
							Row["Alloy_Set_Type"] = "Input"
							# print("Alloy Set (Input)")
							# Row["Alloy_Sets"]["Input"].append(Alloy_Row)
						else:
							Row["Alloy_Set_Type"] = "Button"
							# Row["Alloy_Sets"]["Fixed"].append(Alloy_Row)
							# print("Alloy Set (Fixed)")
						continue
					else:
						Row["Set_Type"] = "Regular_Set"
						# Row["Regular_Sets"]["Input"].append(Set_Row)
						# print("Regular Set (Input)")
				else:
					Row["Set_Type"] = "Regular_Set"
					# Row["Regular_Sets"]["Input"].append(Set_Row)
					# print("Regular Set (Input)")
				Row["All_Unfilled"].append(Unfilled_Set_Dict)

			Last_Set_Index = i.Template.Sets - 1
			Empty_Sets = 4 - i.Template.Sets
			if i.Template.Stop_Set or i.Template.Drop_Set or i.Template.Strength_Drop > 0 or i.Template.Strength_Stop > 0:
				Empty_Sets = 1
				Empty_Sets = 2 - i.Filled_Sets
			if Empty_Sets > 0:
				for n in range(Empty_Sets):
					Row["Empty_Sets"].append("Empty_Set")
			Empty_Sets = 3

			context["Patterns"].append(Row)

# 			ON GET ALLOY PRESS, IDENTIFY WHICH EXERCISE
			if request.GET.get(i.Template.Exercise_Type + "_Get_Alloy"):
				print("Getting Alloy Set for: " + i.Template.Exercise_Type)
				i.Show_Alloy = True
				i.save()
				Get_Alloy_Pressed = True
				request.session["Show_Alloy_Type"] = i.Template.Exercise_Type
			# if((i.Template.Exercise_Type + "_Get_Set") in request.GET.keys()):
			# 	print(i.Template.Exercise_Type + " Get Set is here")
			if request.GET.get(i.Template.Exercise_Type + "_Get_Set"):
				print("Getting SS Set for: " + i.Template.Exercise_Type)
				Get_Set_SS = True
				request.session["SS_Type"] = i.Template.Exercise_Type
			elif request.GET.get(i.Template.Exercise_Type + "_Get_Drop"):
				print("Getting SD Set for: " + i.Template.Exercise_Type)
				Get_Set_SD = True
				request.session["SD_Type"] = i.Template.Exercise_Type
				# return HttpResponseRedirect("/userpage")

#		CHECK IF ALLOYS HAVE BEEN COMPLETED (Show "Submit Workout" button) 
		if Alloys_Complete:
			context["Alloys_Complete"] = ["Yes"]
		else:
			context["Alloys_Complete"] = []


# 		FORM SUBMIT-CHECK STARTS HERE
		Last_Filled_Set = ["", "", "", "", ""]
		if request.GET.get("Submit_Workout") or Get_Alloy_Pressed or Get_Set_SS or Get_Set_SD:
			print("578")
			# print(request.GET.keys())
# 			LOOPING THROUGH SETS
			for _Sub in _Workout.SubWorkouts.all():
				Set_Stats = ""
				Alloy_Sub = False
				if Alloy_Workout and _Sub.Template.Alloy_Reps != 0 and _Sub.Template.Alloy_Reps != None:
					Alloy_Sub = True
				_E_Type = _Sub.Template.Exercise_Type
				_E_Name = _Sub.Exercise.Name				
				if "Carry" in _E_Name:
					Carry_True = True
				else:
					Carry_True = False

				_Stat_, Created = Stat.objects.get_or_create(Type=_E_Type, Member=_Member)

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

				if re.search("-", _Sub.Template.Reps) != None:
					_Reps = _Sub.Template.Reps.split("-")[1]
					print("Reps: " + _Sub.Template.Reps)
				else:
					_Reps = _Sub.Template.Reps

#				REGULAR UNFILLED SETS HANDLED HERE (NON-ALLOY)
				Unfilled = False
				for n in range(Unfilled_Sets_Shown):
					print("Looping through unfilled sets: " + _Sub.Template.Exercise_Type)
					if re.search("-", _Sub.Template.Reps) != None:
						_Reps = _Sub.Template.Reps.split("-")[n + _Sub.Filled_Sets]

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
						# print("FILLED SET: " + )
						print("Stat Max: " + str(_Stat_.Max) + " " + _Stat_.Type)
						if Alloy_Sub:
							Set_Label = "A" + str(n + 1)
						else:
							Set_Label = "R" + str(n + 1)
						Set_Label + "," + _Reps + "," + _Weight + "," + _RPE + "," + _Tempo	
						Last_Filled_Set = (Set_Label + "," + _Reps + "," + _Weight + "," + _RPE + "," + _Tempo).split(',')
					else:
						Unfilled = True

					if _Weight == "":
						if _Sub.Dropped:
							_Weight = _Sub.Drop_Weight
						else:
							_Weight = _Sub.Suggested_Weight

					Stats = Set_Label + "," + _Reps + "," + str(_Weight) + "," + _RPE + "," + _Tempo + "/"
					Set_Stats += Stats

				Set_List = Set_Stats.split("/")
				if '' in Set_List:
					Set_List.remove('')
				print("Set_List: " + str(Set_List))

#				ADDING FILLED SETS TO SUBWORKOUT SET STRING 
				_Sub.Set_Stats += "/" + "/".join(Set_List)
				_Sub.save()
				# if _Sub.Filled_Sets + 1 < 6:
				# 	_Sub.Maxed_Sets = False
				# 	_Sub.save()
				# else:
				# 	_Sub.Maxed_Sets = True
				# 	_Sub.save()

				Last_Set = ["", "", "", "", ""]
				if len(Set_List) >= 1: 
					Last_Set = Set_List[-1].split(",")
					print("Got Last Set: " + _Stat_.Type)
					print("Reps: " + _Sub.Template.Reps)
					print(Unfilled)
				Last_Set = Last_Filled_Set
				if _Sub.Template.Reps != "" and _Sub.Template.Reps != "0" and _Sub.Template.Reps != "B" and not Carry_True:
					print("THIS SHOULD ACTIVATE")
					if not Unfilled:
						print("Not Unfilled: " + _Stat_.Type)
					_Reps_Estimate = int(_Reps)
					_Weight_Estimate = _Sub.Suggested_Weight
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

					if (not StrengthStop and not StrengthDrop and _Stat_.Max == 0) and not Unfilled and _Weight_Estimate != 0 and _Reps_Estimate != 0:
						if _Sub.Template.Reps != "" and _Sub.Template.Reps != "0" and _Sub.Template.Reps != "B":
							print("Setting New Max")
							_Stat_.Max = Get_Max(_Weight_Estimate, _Reps_Estimate, _RPE_Estimate)
							_Stat_.save()

					# 	if Last_Set[3] =="X" or Last_Set[3] == "10":
					# 		Sub.Sets += 1
					# 	else:

						# return HttpResponseRedirect("/userpage")
				if Get_Set_SS and request.session["SS_Type"] == _Sub.Template.Exercise_Type:	
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
 
				if Get_Set_SD and request.session["SD_Type"] == _Sub.Template.Exercise_Type:		
				# if Get_Set_SS and request.session["SS_Type"] == _Sub.Template.Exercise_Type:	
					print("DROP SET BUTTON PRESSED!!!!")
					# _Stat.Alloy_Weight = Get_Weight(_Stat.Max, _Sub.Template.Alloy_Reps + 1, 10)
					# _Stat.save()
					# return HttpResponseRedirect("/userpage")
					if _Sub.Maxed_Sets:
						return HttpResponseRedirect("/userpage")
					else:
						if Last_Set[3] != "" and (float(Last_Set[3]) >= float(_Sub.Template.RPE) or Last_Set[3] == "X"):
							if not _Sub.Dropped:
								print("FIRST DROP")
								# _Sub.Suggested_Weight = _Sub.Suggested_Weight*(100 - _Sub.Template.Strength_Drop)
								_Sub.Drop_Sets += 1
								_Sub.Dropped = True
								_Sub.Stopped = False
								_Sub.save()
							elif _Sub.Dropped:
								print("SECOND DROP")
								_Sub.Stopped = True
								_Sub.save()
							return HttpResponseRedirect("/userpage")
						else:
							# _Sub.Dropped = False
							# _Sub.save()
							return HttpResponseRedirect("/userpage")
					return HttpResponseRedirect("/userpage")
# 				SHOW ALLOY SET + GETTING ALLOY WEIGHT
				if Get_Alloy_Pressed and request.session["Show_Alloy_Type"] == _Sub.Template.Exercise_Type:
					print("Line 854 Executing")
					_Sub.Alloy_Weight = Get_Weight(_Stat_.Max, _Sub.Template.Alloy_Reps + 1, 10)
					_Sub.save()
					print("New Alloy Weight for : " + str(_Sub.Alloy_Weight) + _Sub.Template.Exercise_Type)

# 				ALLOY SET SUBMISSIONS HANDLED HERE
				elif request.GET.get("Submit_Workout") or (Get_Alloy_Pressed 
				and request.session["Show_Alloy_Type"] != _Sub.Template.Exercise_Type):
					# print("Line 803 Executing")
					if Alloy_Sub and _Sub.Show_Alloy:
						_Rep_Code = _Sub.Template.Exercise_Type + "Alloy_Set_Reps"
						print("Alloy Set Rep Code: " + _Rep_Code)
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
							Performed_Reps = request.GET[_Rep_Code]
							_Weight = _Sub.Alloy_Weight
							print(int(Performed_Reps))
							if int(Performed_Reps) <= 20:
								_Stat.Max = Get_Max(_Weight, int(Performed_Reps), 10)
								_Stat.save()
								print("New Max: " + str(_Stat.Max))
							if int(Performed_Reps) >= _Sub.Template.Alloy_Reps:
								_Stat_.Level_Up = True
								_Stat_.Failed = False
								_Stat_.save()
								_Sub.Alloy_Passed = True
								_Sub.save()
							elif int(Performed_Reps) < _Sub.Template.Alloy_Reps:
								_Stat_.Level_Up = False
								_Stat_.Failed = True
								_Stat_.save()
								_Sub.Alloy_Passed = False
								_Sub.save()
							# 	ADD TO SUBWORKOUT SET STATS STRING
							Set_Label = "A" + str(_Sub.Template.Sets)
							Stat_String = Set_Label + "," + str(Performed_Reps) + "," + str(_Weight) + ",10," + Tempo
							Stat_List = Stat_String.split("/")
							if '' in Stat_List:
								Stat_List.remove('')
							_Sub.Set_Stats += "/" + Stat_String
							_Sub.save()
#			WORKOUT SUBMITTED 
			if request.GET.get("Submit_Workout"):
				print("Submitted")
				_Workout.Completed = True
				_Workout.save()
#			LAST WORKOUT/LEVEL-UP CHECK 
				if _Workout.Template.Last:	
					print("Last Workout Submitted")				
					request.session["Level_Up"] = Check_Level_Up(_Member)			
					_Member.Finished_Workouts = True
					_Member.save()		
					_Workout.Completed = True
					_Workout.save()
					return HttpResponseRedirect("/progress-report")
					# elif _Workout.Template.Block_End:
					# 	return HttpResponseRedirect("/next-block")

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
			return HttpResponseRedirect("/userpage")
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
					subworkout_counter += 1

		return HttpResponse('success'); 

Days_Of_Week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

@user_passes_test(Inside_Access, login_url="/")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
def Contact_And_Support(request): 
	return render(request, "contact.html")

@user_passes_test(Inside_Access, login_url="/")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
def Logout(request): 
	logout(request)
	return HttpResponseRedirect("/")

@user_passes_test(Inside_Access, login_url="/")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
def Exercise_Descriptions(request):
	context = {}
	return render(request, "exercise_descriptions.html", context)

@user_passes_test(Inside_Access, login_url="/")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
def Tutorial(request):
	context = {}
	return render(request, "tutorial.html", context)


@user_passes_test(Inside_Access, login_url="/")
@user_passes_test(Member_Not_Expired, login_url="/renew-membership")
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
