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
from Shared_Functions import User_Check, Member_Exists
from RPE_Dict import RPE_Dict
import re
from Shared_Functions import User_Ref_Dict

Days_Of_Week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def Generate_Workouts(Start_Date, Level, Days_List, Member):
	Week_Days = enumerate(Days_Of_Week)
	# Days = Days_List[]
	# Workouts = Workout_Template.objects.get(Level=Level)
	Max_Days = 28
	Output = []
	count = 0
	Days = Days_List
	if Level <= 5:
		if len(Days_List) == 4:
			Days = Days_List[:-1]
		else:
			Days = Days_List
		print("Program Start Date: " + Start_Date.strftime('%m/%d/%Y'))		
		print("Selected Workout Days: ")		
		_Days = []
		for x in Days:
			_Days.append(Days_Of_Week[x])
		print(_Days)

		for i in range(0, 28): #i will be from 1 to 28
			if (Start_Date + timedelta(days=i)).weekday() in Days:
				Workout_Date = Start_Date + timedelta(days=i)
				count += 1				
				string_date = Workout_Date.strftime('%m/%d/%Y')
				_Workout_Template = Workout_Template.objects.get(Level_Group=1, Ordered_ID=count)
				# print("Workout Template: " + "Week " + str(_Workout_Template.Week) + " Day " 
				# + str(_Workout_Template.Day) + " Ordered ID: " + str(_Workout_Template.Ordered_ID) + " Level Group: " + str(_Workout_Template.Level_Group))				
				_Workout = Workout(Template=_Workout_Template, _Date=string_date, Level = Level, Member=Member)
				_Workout.save()
				for x in _Workout.Template.SubWorkouts.all():
					x.Exercise, Created = Exercise.objects.get_or_create(Type = _Type, Level = Level)
					x.save()
					_SubWorkout = SubWorkout(Template = x)
					_SubWorkout.save()
					_Workout.SubWorkouts.add(_SubWorkout)
					_Workout.save()
				print("Level " + str(_Workout.Level) + " Workout Created For: " + _Workout._Date + " (Week " + str(_Workout.Template.Week) + " Day " + str(_Workout.Template.Day) + ")")
				# print(string_date)
				Output.append(string_date)
				# Member.workouts.add(_Workout)
				# Member.save()
		return(Output)
	elif Level <= 10:
		if len(Days_List) == 4:
			Days = Days_List[:-1]
		else:
			Days = Days_List
		Max_Days = 28
		for i in range(0, Max_Days): #i will be from 1 to 28
			if (Start_Date + timedelta(days=i)).weekday() in Days:
				Workout_Date = Start_Date + timedelta(days=i)
				count += 1				
				string_date = Workout_Date.strftime('%m/%d/%Y')
				_Workout_Template = Workout_Template.objects.get(Level_Group=2, Ordered_ID=count)
				_Workout = Workout(Template=_Workout_Template, _Date=string_date, Level = Level, Member=Member)
				_Workout.save()
				for x in _Workout.Template.SubWorkouts.all():
					_SubWorkout = SubWorkout(Template = x)
					_SubWorkout.save()
					_Workout.SubWorkouts.add(_SubWorkout)
					_Workout.save()
				Output.append(string_date)
		return(Output)
	elif Level <= 15: #9 Weeks
		Max_Days = 63
		for i in range(0, Max_Days): #i will be from 1 to 28
			if (Start_Date + timedelta(days=i)).weekday() in Days:
				Workout_Date = Start_Date + timedelta(days=i)
				count += 1				
				string_date = Workout_Date.strftime('%m/%d/%Y')
				if count <= 16:
					_Workout_Template = Workout_Template.objects.get(Level_Group=3, Ordered_ID=count, Block_Num=1)
					_Workout = Workout(Template=_Workout_Template, _Date=string_date, Level = Level, Member=Member)
					for x in _Workout.Template.SubWorkouts.all():
						_SubWorkout = SubWorkout(Template = x)
						_SubWorkout.save()
						_Workout.SubWorkouts.add(_SubWorkout)
					_Workout.save()
				elif count > 16 and count < 36:
					adjusted_count = count - 16
					_Workout_Template = Workout_Template.objects.get(Level_Group=3, Ordered_ID=adjusted_count, Block_Num=2)
					_Workout = Workout(Template=_Workout_Template, _Date=string_date, Level = Level, Member=Member)
					for x in _Workout.Template.SubWorkouts.all():
						_SubWorkout = SubWorkout(Template = x)
						_SubWorkout.save()
						_Workout.SubWorkouts.add(_SubWorkout)
					_Workout.save()
				Output.append(string_date)
		return(Output)
	elif Level <= 25: #9 Weeks
		Max_Days = 63
		for i in range(0, Max_Days): #i will be from 1 to 28
			if (Start_Date + timedelta(days=i)).weekday() in Days:
				Workout_Date = Start_Date + timedelta(days=i)
				count += 1				
				string_date = Workout_Date.strftime('%m/%d/%Y')
				if count <= 16:
					_Workout_Template = Workout_Template.objects.get(Level_Group=4, Ordered_ID=count, Block_Num=1)
					_Workout = Workout(Template=_Workout_Template, _Date=string_date, Level = Level, Member=Member)
					_Workout.save()
					for x in _Workout.Template.SubWorkouts.all():
						_SubWorkout = SubWorkout(Template = x)
						_SubWorkout.save()
						_Workout.SubWorkouts.add(_SubWorkout)
						_Workout.save()
				elif count > 16:
					adjusted_count = count - 16
					_Workout_Template = Workout_Template.objects.get(Level_Group=4, Ordered_ID=adjusted_count, Block_Num=2)
					_Workout = Workout(Template=_Workout_Template, _Date=string_date, Level = Level, Member=Member)
					_Workout.save()
					for x in _Workout.Template.SubWorkouts.all():
						_SubWorkout = SubWorkout(Template = x)
						_SubWorkout.save()
						_Workout.SubWorkouts.add(_SubWorkout)
						_Workout.save()
				Output.append(string_date)
		return(Output)


@user_passes_test(User_Check, login_url="/")
def Get_Workout_Block(request):
	context = {}
	Days_List = []
	Ref_Dict = User_Ref_Dict(request.user)
	context["Level"] = Ref_Dict["Level"]
	context["Num_Days"] = 3

	_Member = Ref_Dict["Member"]
	_Member.Level = 13
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
			Generate_Workouts(Start_Date, _Level, Days_List, _Member)
			return HttpResponseRedirect("/userpage")
	return render(request, "next_workout_block.html", context)
