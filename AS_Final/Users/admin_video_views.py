# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
from django.contrib.auth import logout, login, authenticate
from django.core.files import File
from .views import Levels, Exercise_Types
from django.contrib.auth.decorators import user_passes_test
import os
import json
import stripe
from checks import Admin_Check

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Videos(request):
	context = {}
	context["Video_Display"] = []
	context["Video_Display_Test"] = ["videos/Dashboard_Shot.png", 1]
	context["Exercise_Types"] = ["UB Hor Push", "Hinge", "Squat", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "LB Uni Push", 
	"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2"]
	context["Levels"] = Levels
	context["Level_Display"] = []
	# context["Level_Access_Options"] = ["0"]
	if "Current_Exercises" not in request.session.keys():
		request.session["Current_Exercises"] = []

	for i in Video.objects.all():
		# i.delete()
		row = []
		_Type = i.Exercise_Type
		_Image_URL = "/" + i.File.url
		_Thumbnail_URL = i.Get_Thumbnail()
		row.append(i.Title)
		_Name = i.File.name.replace("static/videos/", "")
		print("File Name: " + i.File.name)
		print("File URL: " + i.File.url)
		_URL = i.File.url.replace("static/", "")
		# row.append(_URL)
		row.append(_URL)
		row.append("videos/Dashboard_Shot.png")
		row.append(i.File.url)
		row.append(_Image_URL)
		row.append(_Thumbnail_URL)
		row.append(_Type)
		Exercise_Names = []
		for x in i.Exercises.all():
			Exercise_Names.append(x)
		row.append(Exercise_Names)
		context["Video_Display"].append(row)

	if request.method == "POST":
		Selected_Exercise = request.POST['Exercise']
		print(request.POST['Exercise'])
		request.session["Exercise"] = request.POST['Exercise']
		# return HttpResponseRedirect("/admin-videos")

	if request.POST.get("Clear"):
		for i in Video.objects.all():
			i.delete()
		return HttpResponseRedirect("/admin-videos")

	# if request.POST.get("Level"):
	# 	print("LEVEL SELECTED: " + request.POST['Level'])
	# 	request.session["Level"] = int(request.POST['Level'])

	if "Exercise" not in request.session.keys():
		request.session['Exercise'] = "UB Hor Push"
	
	if "Exercise" in request.session.keys():
		_Type = request.session['Exercise']
		context["Selected_Exercise"] = [_Type]
		context["Exercise_Types"].remove(_Type)

		print("Selected Exercise: " + request.session['Exercise'])
		_Exercises = Exercise.objects.filter(Type = _Type)
		for n in Levels:
			if Exercise.objects.filter(Type = _Type, Level = n).exists():
				_Exercise = Exercise.objects.get(Type=_Type, Level = n)
				context["Level_Display"].append([str(n) + " (" + _Exercise.Name + ")", _Exercise.Name])
	else:
		context["Level_Display"] = Levels

	if request.POST.get("AddExercises"):
		print("AddExercises Pressed")
		Add_Exercises = request.POST.getlist("Exercise_List")
		for i in Add_Exercises:
			if i not in request.session["Current_Exercises"]:
				request.session["Current_Exercises"].append(i)
		print("Add Exercises: " + str(Add_Exercises))

	context["Current_Exercises"] = request.session["Current_Exercises"]

	if request.POST.get("VideoUploadSubmit"):
		# cwd = os.getcwd()
		# print(str(request.GET.get("VideoUpload")))
		# _File = request.GET.get("VideoUpload")
		_F = request.FILES['VideoUpload']
		print("_F: " + str(_F.name))
		_File = File(_F)
		print("File: " + str(_File.name))
		_Video = Video(Title="Test")
		_Video.File = _File
		_Video.save()		

		# _File = File(open(request.POST.get("VideoUpload"), 'w+'))	
		# print(_File.name)
		# print("Upload button pressed. File Name: " + _File.name)
		return HttpResponseRedirect("/admin-videos")

	if request.POST.get("AddVideo"):
		_Title = request.POST.get("Title")
		_File = File(request.FILES['VideoUpload'])
		_Type = request.POST['Exercise']
		_Tags = ""
		if 'Tags' in request.POST.keys():
			_Tags = request.POST['Tags']

		if "Thumbnail" in request.FILES.keys():
			_Thumbnail = File(request.FILES['Thumbnail'])
			No_Thumbnail = False
		else:
			Default_Thumbnail = open("static/videos/Thumbnails/Default_Thumbnail.png", "r")
			_Thumbnail = File(Default_Thumbnail)
			No_Thumbnail = True

		_Description = ""
		if "Description" in request.POST.keys():
			_Description = request.POST['Description']
		print(_Description)
		Level_Access = request.POST["Level_Access"]
		print(_Title)

		_Video = Video(Title = _Title, File = _File, Exercise_Type=_Type, Description=_Description, Tags=_Tags)

		if No_Thumbnail:
			_Video.Default_Thumbnail_URL = "/static/videos/Thumbnails/Default_Thumbnail.png"
		else:
			_Video.Thumbnail = _Thumbnail
			_Video.Has_Thumbnail = True
		# _Video.Thumbnail.url = "static/videos/Thumbnails/Default_Thumbnail.png"
		Add_Exercises = request.POST.getlist("Exercise_List")
		_Video.Level_Access = Level_Access
		_Video.save()
		for i in Add_Exercises:
			_Exercise = Exercise.objects.get(Name = i)
			_Video.Exercises.add(_Exercise)
			_Video.save()
		request.session["Uploading_Video_PK"] = _Video.pk

		return HttpResponseRedirect("/admin-videos-library")
	return render(request, "adminvideos.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Videos_2(request):
	context = {}
	_Video = Video.objects.get(pk=request.session["Uploading_Video_PK"])
	_Thumbnail_URL = _Video.Get_Thumbnail()
	_Video_URL = "/" + _Video.File.url
	_Title = _Video.Title
	_Exercises = _Video.Exercises.all()

	context["Video_Title"] = _Title
	context["Thumbnail_URL"] = _Thumbnail_URL
	context["Video_URL"] = _Video_URL
	context["Assigned_Exercises"] = []

	for i in _Exercises:
		context["Assigned_Exercises"].append([i.Name, i.Video_Description])

	if request.POST.get("UpdateDescriptions"):
		for i in _Exercises:
			if request.POST["Description" + i.Name] != "":
				i.Video_Description = request.POST["Description" + i.Name]
				i.save()
		return HttpResponseRedirect("admin-videos-2")

	# if request.POST.get("Submit_Btn"):
	# 	return HttpResponseRedirect("admin-videos-library")

	return render(request, "adminvideos2.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Videos_Library(request):
	context = {}
	context["Videos"] = []

	for v in Video.objects.all():
		row = []
		_Exercises = v.Exercises.all()
		exercises_row = []
		
		for i in _Exercises:
			exercises_row.append([i.Name, i.Video_Description])
			# exercises_row.append(i.Video_Description)

		_Thumbnail_URL = v.Get_Thumbnail()
		row.append(_Thumbnail_URL)
		row.append(v.Title)
		row.append(v.pk)
		row.append("Edit" + v.Title + str(v.pk)) #3 is button code
		_Tags = v.Tags.split(',')
		Tags = ""
		for _Tag in _Tags:
			Tags = Tags + " , " + _Tag
		row.append(Tags) #4 is tags
		row.append(exercises_row) #5 is exercises
		row.append(v.Level_Access) #6 is Level Access
		context["Videos"].append(row)

	if request.GET.get("Delete"):
		print("Delete Button Pressed")
		Delete_PK = request.GET["Delete_PK"]
		print("Delete PK: " + str(Delete_PK))
		Delete_Video = Video.objects.get(pk=Delete_PK)
		Delete_Video.delete()
		print("Deleting")
		# Delete_Video.Exercises.clear()
		if os.path.isfile(Delete_Video.File.url):
			 os.remove(Delete_Video.File.url)
			 print("Removed Video File")
		if Delete_Video.Has_Thumbnail:
			if os.path.isfile(Delete_Video.Thumbnail.url):
				 os.remove(Delete_Video.Thumbnail.url)
				 print("Removed Video File")
		# if os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),_Video.file.url)):
		# 	 os.remove(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),_Video.file.url))
		# 	 print("Removed Video File")
		return HttpResponseRedirect("/admin-videos-library")

	if request.method == 'POST' and not request.POST.get("Delete"):
		# for key in request.GET:
		# 	print("Request Object: " + request.GET[key])
		Keys = []
		for i in request.POST.keys():
			Keys.append(i)
			# print("Key: " + i)
			# print("Key: " + i)
			# print(type(i))
			# if i is int:
			# 	print("Int Key: " + i)
			# if i is str:
			# 	print("String Key: " + i)
				# print("Request Value: " + request.POST[i])
				# request.session["Video_PK"] = int(i)
		# print(request.GET)
		print("First Key: " + Keys[0])
		print("Second Key: " + Keys[1])
		print("REQUEST RECEIVED: ")
		if Keys[1] != 'csrfmiddlewaretoken':
			request.session["Video_PK"] = int(Keys[1])
		else:
			request.session["Video_PK"] = int(Keys[0])
		return HttpResponseRedirect("/admin-videos-library-edit")
	return render(request, "adminvideoslibrary.html", context)

@user_passes_test(Admin_Check, login_url="/admin-login")
def Admin_Videos_Edit(request):
	context = {}
	_Video = Video.objects.get(pk=request.session["Video_PK"])
	_Type = _Video.Exercise_Type
	_Exercise_List = Exercise.objects.filter(Type=_Type)
	_Assigned_Exercises = _Video.Exercises.all()
	context["Display"] = []
	_Thumbnail_URL = _Video.Get_Thumbnail()
	_Video_URL = "/" + _Video.File.url

	context["Display"].append(_Thumbnail_URL) 
	context["Display"].append(_Video.Exercise_Type)
	context["Exercise_Types"] = Exercise_Types
	context["Exercise_List"] = []
	context["Assigned_Exercises"] = []
	context["Video_URL"] = _Video_URL
	context["Description"] = _Video.Description
	context["Tags"] = _Video.Tags.split(",")
	context["Video_Title"] = _Video.Title

	context["Levels"] = Levels
	context["Level_Access"] = _Video.Level_Access

	context["Exercise_Description_Types"] = [["None", ""],
	["Romanian Deadlift", "#RDL"],
	["Barbell Deadlift", "#BBDL"],
	["Goblet Squat", "#Squat_Goblet"],
	["UB Hor Pull", "#UBHPull"],
	["Bench Press", "#Bench_Press"],
	["Floor Press", "#Floor_Press"],
	["UB Vert Push", "#UBVPush"],
	["Band Pullapart", "#Accessory_Band_Pullapart"]]

	Describer_Labels_Dict = {
	}
	for x in context["Exercise_Description_Types"]:
		Describer_Labels_Dict[x[1]] = x[0]
	# print("Test")
	# print("PK from Edit: " + str(request.session["Video_PK"]))
	for i in _Exercise_List:
		if i not in _Video.Exercises.all():
			row = []
			row.append(i.Name)
			row.append(i.Level)
			row.append(i.pk)
			context["Exercise_List"].append(row)
	for i in _Assigned_Exercises:
		row = []
		row.append(i.Name)
		row.append(i.Level)
		row.append(i.pk)
		row.append(i.Video_Description)
		if i.Description_Code == "":
			row.append("None")
		else:
			row.append(Describer_Labels_Dict[i.Description_Code])
		context["Assigned_Exercises"].append(row)

	if request.GET.get("Change_Level_Access"):
		_Access = request.GET["Level_Access"]
		_Video.Level_Access = _Access
		_Video.save()
		return HttpResponseRedirect("/admin-videos-library-edit")

	if request.POST.get("Change_Title"):
		New_Title = request.POST["New_Title"]
		print(New_Title)
		_Video.Title = New_Title
		_Video.save()
		return HttpResponseRedirect("/admin-videos-library-edit")

	if request.GET.get("Change_Type_Btn"):
		New_Type = request.GET["Change_Type"]
		_Video.Exercise_Type = New_Type
		_Video.save()
		return HttpResponseRedirect("/admin-videos-library-edit")

	if request.method == "POST":
		print("POST REQUEST DETECTED")
		if request.POST.get("Edit_Video"):
			print("Edit Video")
			if "VideoUpload" in request.FILES.keys():
				print(request.FILES["VideoUpload"])
			# if request.FILES["VideoUpload"] != None:
				_Video_File = File(request.FILES['VideoUpload'])
				_Video.File = _Video_File
				_Video.save()			
		if request.POST.get("Edit_Thumbnail"):
			print("Edit Thumbnail")
			if "ThumbnailUpload" in request.FILES.keys():
				print(request.FILES["ThumbnailUpload"])
			# if request.FILES["ThumbnailUpload"] != None:
				_Thumbnail_File = File(request.FILES['ThumbnailUpload'])
				_Video.Thumbnail = _Thumbnail_File
				_Video.save() 
		if request.POST.get("Add_Tag"):
			print("Add Tag")
			_Video.Tags = _video.Tags + "," + request.POST["Tag"]
		return HttpResponseRedirect('/admin-videos-library-edit')

	if request.GET.get("RemoveExercises"):
		PKs = request.GET.getlist("Remove_Exercises")
		for i in PKs:
			_Exercise = Exercise.objects.get(pk=i)
			_Video.Exercises.remove(_Exercise)
			_Video.save()
		return HttpResponseRedirect('/admin-videos-library-edit')

	if request.GET.get("Update_Descriptions"):
		for i in _Assigned_Exercises:
			Describer_Code = str(i.pk) + "_Describer"
			if request.GET.get(Describer_Code):
				i.Description_Code = request.GET[Describer_Code]
				i.save()
			if request.GET.get(str(i.pk) + "_Description"):
				i.Video_Description = request.GET[str(i.pk) + "_Description"]
				i.save()
			else:
				i.Video_Description = ""
				i.save()
		if request.GET.get("General_Description"):
			_Video.Description = request.GET["General_Description"]
			_Video.save()
		return HttpResponseRedirect('/admin-videos-library-edit')

	if request.GET.get("AddExercises"):
		print("Test Submit")
		PKs = request.GET.getlist("Assign_Exercises")
		print(PKs)
		for i in PKs:
			print(i)
			_Exercise = Exercise.objects.get(pk=i)
			_Video.Exercises.add(_Exercise)
			_Video.save()
		return HttpResponseRedirect('/admin-videos-library-edit')

	if request.POST.get("Edit_Video"):
		_File = File(request.FILES['VideoUpload'])
		_Video.File = _File
		_Video.save()

	if request.POST.get("Edit_Thumbnail"):
		_Thumbnail = File(request.FILES['ThumbnailUpload'])
		_Video.Thumbnail = _Thumbnail
		_Video.save()

	if request.GET.get("Delete_Video"):
		_Video.delete()
		if os.path.isfile(_Video.File.url):
			 os.remove(_Video.File.url)
			 print("Removed Video File")
		if _Video.Has_Thumbnail:
			if os.path.isfile(_Video.Thumbnail.url):
				 os.remove(_Video.Thumbnail.url)
				 print("Removed Thumbnail")
		# if os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),_Video.file.url)):
		# 	 os.remove(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),_Video.file.url))
		# 	 print("Removed Video File")

		return HttpResponseRedirect('/admin-videos-library')

	return render(request, "adminvideosedit.html", context)
