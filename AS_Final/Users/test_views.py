# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
import json
import stripe

def Test(request):
	context = {}
	context["Days_Of_Week"] = [["Monday", 0],["Tuesday", 1], ["Wednesday", 2], ["Thursday", 3], ["Friday", 4], ["Saturday", 5], ["Sunday", 6]]
	if request.GET.get("Create_Workout"):
		_Level = int(request.GET.get("Level"))
		_Year = request.GET.get("Year")
		_Month = request.GET.get("Month")
		_Day = request.GET.get("Day")

		Day_1 = int(request.GET.get("Day_1"))
		Day_2 = int(request.GET.get("Day_2"))
		Day_3 = int(request.GET.get("Day_3"))

		print(Day_1)
		print(Day_2)
		print(Day_3)

		Year = int(_Year)
		if _Month[0] == '0':
			Month = int(_Month[1])
		else:
			Month = int(_Month)
		if _Day[0] == '0':
			Day = int(_Day[1])
		else:
			Day = int(_Day)

		_Workout_Templates = Workout_Template.objects.filter(Level_Group = 1)

		for i in _Workout_Templates:
			print("Existing Workout Template: " + "Week " + str(i.Week) + " Day " 
			+ str(i.Day) + " Ordered ID: " + str(i.Ordered_ID) + " Level Group: " + str(i.Level_Group))

		print(_Level)
		print(Year)
		print(Month)
		print(Day)

		print(Generate_Workouts(datetime(Year, Month, Day), _Level, [Day_1, Day_2, Day_3]))
		return HttpResponseRedirect('/test/')
	return render(request, "test.html", context)
