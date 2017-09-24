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
from RPE_Dict import *
from Shared_Functions import User_Check, Member_Exists

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

Level_Names = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12", "Level 13", "Level 14", "Level 15",
"Level 16", "Level 17", "Level 18", "Level 19", "Level 20", "Level 21", "Level 22", "Level 23", "Level 24", "Level 25"]


@user_passes_test(User_Check, login_url="/")
def Videos_2(request): 
	context = {}
	return render(request, "videos_2.html", context)

@user_passes_test(User_Check, login_url="/")
def Videos(request): 
	# _User = request.user
	# _Member = Member.objects.get(User = _User)
	# _Level = Member.Level
	context = {}
	context["Videos"] = []
	context["Levels"] = Levels

	context["Current_Level"] = []

	context["Display_Levels"] = Level_Names

	context["Video_Group_1"] = []
	context["Video_Group_2"] = []
	context["Video_Group_3"] = []
	context["Video_Group_4"] = []
	context["Video_Group_5"] = []

	_Exercises = Exercise.objects.all()
	_Videos = Video.objects.all()

	# if 'Current_Level' in request.session.keys():
	# 	context["Current_Level"] = [request.session["Current_Level"]]

	for i in _Exercises:
		if i.Level <= 5:
			context["Video_Group_1"].append(i.Name)
		elif i.Level <= 10:
			context["Video_Group_2"].append(i.Name)
		elif i.Level <= 15:
			context["Video_Group_3"].append(i.Name)
		elif i.Level <= 20:
			context["Video_Group_4"].append(i.Name)
		elif i.Level <= 25:
			context["Video_Group_5"].append(i.Name)
		if request.GET.get(str(i.pk)):
			print("PK Submitted: " + str(i.pk) + " " + i.Name)

	context["Video_URL"] = ""

	if "Video_PK" in request.session.keys():
		if Video.objects.filter(pk=request.session["Video_PK"]).exists():
			Selected_Video = Video.objects.get(pk=request.session["Video_PK"])
			context["Video_URL"] = "/" + Selected_Video.File.url
			context["Video_Title"] = Selected_Video.Title
			context["Related_Exercises"] = []
			for i in Selected_Video.exercises.all():
				Dict = {}
				Dict["Name"] = i.Name
				Dict["Description_URL"] = i.Description_Code
				context["Related_Exercises"].append(Dict)

	for i in _Videos:
		row = []
		_Name = i.Title
		_Thumbnail_URL = "/" + i.Thumbnail.url
		row.append(_Name)
		row.append(i.pk)
		row.append(_Thumbnail_URL)
		context["Videos"].append(row)


	for i in _Videos:
		if request.GET.get(str(i.pk)):
			print("Video PK Submitted: " + str(i.pk) + " " + i.Title)
			request.session["Video_PK"] = i.pk
			context["Video_URL"] = "/" + i.File.url
			context["Video_Title"] = i.Title
			return HttpResponseRedirect("/videos")
			# return render(request, "videos.html", context)



	# if request.method == "GET":
		# print("Form Submitted")
		# print("Video PK: " + str(request.GET.get("Video_PK")))
	if request.method == "POST":
		print("POST DETECTED")
		_Name = request.POST["Description_Exercise_Name"]
		print(_Name)
		_Exercise = Exercise.objects.get(Name=_Name)
		context["Selected_Exercise_Description"] = _Exercise.Video_Description
		request.session["Description_Exercise_Name"] = _Name

	if "Description_Exercise_Name" in request.session.keys():
		context["Selected_Exercise_Name"] = [request.session["Description_Exercise_Name"]]
		context["Related_Exercises"].remove(request.session["Description_Exercise_Name"])
	else:
		context["Selected_Exercise_Name"] = []


	if request.GET.get("search_submit"):
		context["Videos"] = []
		_Search_Entry = request.GET.get("search")
		_Search_Terms = _Search_Entry.split()
		_Level_String = request.GET.get("Level")
		# print(_Level_String)
		if (_Level_String != "All Levels"):
			_Level_Split = _Level_String.split()
			_Level = int(_Level_Split[1])
		request.session['Current_Level'] = _Level_String
		context["Current_Level"] = [_Level_String]
		Last_Levels = []
		context["Display_Levels"] = Level_Names	

		# context["Display_Levels"].remove(_Level_String)		
		# if _Level != 0:
			# for i in context["Display_Levels"]:
			# 	if i != _Level_String:
			# 		Last_Levels.append(i)
			# context["Display_Levels"] = []
			# context["Display_Levels"].append(_Level_String)
			# context["Display_Levels"] = context["Display_Levels"] + Last_Levels
		# print("Searching:")
		# print(_Search_Entry)
		# print(_Search_Terms)
		# print(_Level)
		if (_Level_String == "All Levels"):
			context["Display_Levels"] = ["All Levels"] + Level_Names
			print("All Levels Selected")
		if (_Level_String != "All Levels" and _Level != 0):
			_Level_Num = int(_Level)
			_Exercises = Exercise.objects.filter(Level = _Level_Num)
			context["Display_Levels"] = [_Level_String] + Level_Names

		if _Search_Entry == "":
			for i in _Videos:
				row = []
				_Name = i.Title
				_Thumbnail_URL = "/" + i.Thumbnail.url
				row.append(_Name)
				row.append(i.pk)
				row.append(_Thumbnail_URL)
				context["Videos"].append(row)
			# for i in _Exercises:
			# 	_Name = i.Name
			# 	row = []
			# 	row.append(_Name)
			# 	row.append(i.pk)
			# 	context["Videos"].append(row)
			return render(request, "videos.html", context)
		else:
			print("Line 148 Executing")
			for i in _Videos:
				_Tag_List = i.Tags.split(',')
				_Tags = ""
				for t in _Tag_List:
					_Tags = _Tags + t + " "
				_Title = i.Title
				_Check_Against = _Tags + " " + _Title
				_Thumbnail_URL = "/" + i.Thumbnail.url

				for _Term in _Search_Terms:
					if _Term in _Check_Against:
						# context["Videos"].append(_Title)
						context["Videos"].append([_Title, i.pk, _Thumbnail_URL])
					elif _Term.capitalize() in _Check_Against:
						# context["Videos"].append(_Title)
						context["Videos"].append([_Title, i.pk, _Thumbnail_URL])
					elif _Term.lower() in _Check_Against:
						# context["Videos"].append(_Title)
						context["Videos"].append([_Title, i.pk, _Thumbnail_URL])
			# for i in _Exercises:
			# 	_Name = i.Name				
			# 	for _Term in _Search_Terms:
					# print(_Term)
					# print(_Term.lower())
					# print(_Term.capitalize())
					# if _Term in _Name:
					# 	context["Videos"].append(_Name)
					# elif _Term.capitalize() in _Name:
					# 	context["Videos"].append(_Name)
					# elif _Term.lower() in _Name: 
					# 	context["Videos"].append(_Name)
			return render(request, "videos.html", context)
	return render(request, "videos.html", context)
