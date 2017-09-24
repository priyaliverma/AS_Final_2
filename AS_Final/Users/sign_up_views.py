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
from checks import *
from RPE_Dict import *
import re

Days_Of_Week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

Exercise_Types = ["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat", "LB Uni Push", 
"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2"]

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

def Home(request):
	context = {}
	Lift_Names = ["Squat", "Bench", "Deadlift", "Overhead_Press", "Power_Clean", "C_Jerk"]
	context["Login_Failed"] = ""
	context["Signup_Error"] = ""
	Lifts = {}
	Lifts_In_Pounds = {}
	RPE_Experience = False
	print("User: " + str(request.user))
	print("USername: " + request.user.username)
	for i in User.objects.all():
		print("Existing username: " + i.username)

	if request.POST.get("Log_In"):
		print("Log In Button Pressed (Post)")
		_Username = request.POST["Username"]
		_Password = request.POST["Password"]
		print("Username: " + _Username)
		print("Password: " + _Password)
		user = authenticate(username=_Username, password=_Password)
		if user is not None:
			# print("User authenticated")
		    	login(request, user)
			return HttpResponseRedirect('/userpage')
		else:
			print("User not authenticated")
			context["Login_Failed"] = "Login Failed - Please Try Again"
		return render(request, "homepage.html", context)

	
	for i in Lift_Names:
		Lifts[i] = []
		Lifts_In_Pounds[i] = 0
	print("Test Print")

	if request.GET.get("Form_1"):
		print("Form 1 Submitted")
	if request.method == "GET":
		print("Get Request Detected")
	if request.GET.get("Sign_Up"):
		print("Sign Up Button Pressed")

		F_Name = request.GET.get("F_Name")
		L_Name = request.GET.get("L_Name")

		Email = request.GET.get("Email")

		P_Word_1 = request.GET.get("PWord_1")
		P_Word_2 = request.GET.get("PWord_2")
		
		DOB = request.GET.get("DOB")
		
		Training_Months = request.GET.get("TrainingMonths")

		Height = request.GET.get("Height").split(",")
		Weight = request.GET.get("Weight").split(",")

		RPE_Exp = request.GET.get("RPE_Exp")
		print("RPE Experience: " + RPE_Exp)
		if RPE_Exp == "Y":
			RPE_Experience = True

		print("Lifts: ")
		for i in Lift_Names:
			_Lift_Data = request.GET.get(i).split(",")			
			Lifts[i] = _Lift_Data
			if _Lift_Data[0] == "":
				Lifts_In_Pounds[i] = 0
			elif _Lift_Data[1] == "Metric":
				Lifts_In_Pounds[i] = float(_Lift_Data[0])*2.204
			else:
				Lifts_In_Pounds[i] = float(_Lift_Data[0])

		print(Lifts)
		
		print("Lifts In Pounds")
		print(Lifts_In_Pounds)
		for key in Lifts_In_Pounds:
			print(key + " " + str(Lifts_In_Pounds[key]))

		print("Squat Weight in Pounds: " + str(Lifts_In_Pounds["Squat"]))
		print("Height: " + str(Height))
		print("First Name: " + F_Name)
		print("Email: " + Email)
		print("Password 1: " + P_Word_1)
		print("Password 2: " + P_Word_2)
		print("Date of Birth: " + DOB)
		print(Training_Months)

		Bench_Weight = 0
		Squat_Weight = 0
		Body_Weight = 0

		if Lifts_In_Pounds["Bench"] != "None":
			Bench_Weight = Lifts_In_Pounds["Bench"]

		if Lifts_In_Pounds["Squat"] != "None":
			Squat_Weight = Lifts_In_Pounds["Squat"]

		if Weight[1] == "Metric":
			Body_Weight = float(Weight[0])*2.204
		elif Weight[0] != "":
			Body_Weight = float(Weight[0])

		# ASSIGNING LEVEL
		Assigned_Level = 1
		if Squat_Weight < Body_Weight:
			Assigned_Level = 1
		elif Squat_Weight > Body_Weight*1.5 and Bench_Weight > Body_Weight and RPE_Experience:
			Assigned_Level = 11
		else:
			Assigned_Level = 6
		print("Assigned Level: " + str(Assigned_Level))

		if (F_Name != "" and L_Name != "" and Email != "" and P_Word_1 != "" and P_Word_1 == P_Word_2):
			if User.objects.filter(username = Email).exists():
				context["Signup_Error"] = "An account with that email has already been created!"
				print("Sign-up Error")
				return render(request, "homepage.html", context)
			else:
				print("Signing Up...")
				New_User = User.objects.create_user(Email, password=P_Word_1)
				New_User.first_name = F_Name
				New_User.last_name = L_Name
				# User(first_name = F_Name, last_name = L_Name, email= Email, username = Email, password = P_Word_1)
				New_User.save()
				New_Member = Member(User = New_User, Level = Assigned_Level, Squat = Squat_Weight)
				New_Member.New = True
				if New_User.username == "Alloy_Admin":
					New_Member.Admin = True
				New_Member.save()
				user = authenticate(username=Email, password=P_Word_1)
				if user is not None:
				    	login(request, user)
				return HttpResponseRedirect("/sign-up-confirmation")

	if request.POST.get("Sign_Up"):
		print("Sign Up Button Pressed")
		F_Name = request.POST.get("F_Name")
		Email = request.POST.get("Email")
		P_Word_1 = request.GET.get("P_Word_1")
		P_Word_2 = request.GET.get("P_Word_2")
		DOB = request.GET.get("DOB")
		Training_Months = request.POST["TrainingMonths"]
		print(F_Name)
		print(Email)
		print(P_Word_1)
		print(P_Word_2)
		print(DOB)
		print(Training_Months)

	return render(request, "homepage_2.html", context)

@user_passes_test(Member_Exists, login_url="/")
def SignUp_Confirmation(request):
	context = {}
	User = request.user
	_Member = Member.objects.get(User=User)
	stripe.api_key = "sk_test_LKsnEFYm74fwmLbyfR3qKWgb"
	Package_Description = "Gold"
	print("RPE Test: " + str(Get_Weight(200, 8, 8)))

	Packages = [["Gold ($300.00)", "G", 300, timedelta(days=365)], ["Silver ($180.00)", "S", 180, timedelta(days=180)], 
	["Bronze ($40.00)", "B", 40, timedelta(days=30)]]
	request.session["Package"] = "G"
	context["Packages"] = [] 

	Processing_Fee = 0
	context["Processing_Fee"] = Processing_Fee 

	Total = 0
	Subscription_Time = timedelta(days=30)

	for i in stripe.Customer.all():
		print("Stripe Customer: " + str(i.id))

	# if request.POST.get("Payment_Btn"):
	if request.GET.get("Package"):
		Package = request.GET.get("Package")
		print("Package: " + str(Package))
		request.session["Package"] = Package

	# if "Package" not in request.session.keys():
	# 	request.session["Package"] = "G"

	for i in Packages:
		if i[1] == request.session["Package"]:
			context["Packages"].append(i)
			Total = i[2] + Processing_Fee
			context["Total"] = i[2] + Processing_Fee
			Subscription_Time = i[3]
			print(datetime.now())
			print(datetime.now() + i[3])
	for i in Packages:
		if i[1] != request.session["Package"]:
			context["Packages"].append(i)

	Charge_Amount = int(Total*100)

	if request.method == "POST":
		print("Payment POST received")
		Number = request.POST.get("cardnumber")
		print(Number)
		token = request.POST.get('stripeToken') # Using Flask
		print(token)

		try:
			customer = stripe.Customer.create(
				# email=_Username,
				source=token,
			)
			_ID = customer.id
			charge = stripe.Charge.create(
				amount=Charge_Amount, # new_order.total * 100
			    currency="usd",
			    customer=_ID,
			          # source=token,
			    description="Gold",
			    )
			print("New Customer ID: " + str(_ID))
			print("New Customer Charged: " + str(charge.amount))
			_Member.Paid = True
			_Member.Signup_Date = datetime.now()
			_Member.Expiry_Date = datetime.now() + Subscription_Time
			_Member.save()
			print(_Member.Signup_Date)
			print(_Member.Expiry_Date)
			# print("New Customer Charged! " + str(_ID) + " Amount: " + str(charge.amount))
			return HttpResponseRedirect("/welcome")

		except stripe.error.CardError:
			print("Card Error - PAYMENT DECLINED")
			context["Payment_Status"] = "Payment Failed!"
			return render(request, "signup_confirmation.html", context)


	if request.GET.get("Payment_btn"):
		print("Payment Button Pressed")
		return HttpResponseRedirect("/Welcome")
	return render(request, "signup_confirmation.html", context)

def Generate_Workouts(Start_Date, Level, Days_List, Member):
	Week_Days = enumerate(Days_Of_Week)
	# Days = Days_List[]
	# Workouts = Workout_Template.objects.get(Level=Level)
	Output = []
	if Level <= 5:
		if len(Days_List) == 4:
			Days = Days_List[:-1]
		else:
			Days = Days_List
		# Create workout objects with dates according to the next 4 weeks
		# 1. Get day of the week of start_date (should be one of Days_List)
		# 	Give member option to choose one of the 3-4 Days to start on
		# 2. Get all workout days...
		# Order the workouts
		# _Templates = Workout_Template.objects.filter(Level_Group = 1)

		# for i in _Templates:
		# 	print("Existing Workout Template: " + "Week " + str(i.Week) + " Day " 
		# 	+ str(i.Day) + " Ordered ID: " + str(i.Ordered_ID) + " Level Group: " + str(i.Level_Group))
		count = 0
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
					_Type = x.Exercise_Type
					# _Weight = Get_Weight(Max, x.Reps, x.RPE)
					x.Exercise, Created = Exercise.objects.get_or_create(Type = _Type, Level = Level)
					x.save()
					_Workout.SubWorkouts.add(x)
					_Workout.save()
				print("Level " + str(_Workout.Level) + " Workout Created For: " + _Workout._Date + " (Week " + str(_Workout.Template.Week) + " Day " + str(_Workout.Template.Day) + ")")
				# print("Sets and Reps: ")
				for z in _Workout.SubWorkouts.all():
					print(z.Exercise.Name + " " + str(z.Sets) + " x " + str(z.Reps))
				# print(string_date)
				Output.append(string_date)
				# Member.workouts.add(_Workout)
				# Member.save()
		return(Output)
	elif Level >= 6 and Level <= 10:
		return None
	elif Level >= 11 and Level <= 15:
		return None
	elif Level >= 16 and Level <= 25:
		return None
			# .weekday(timedelta(days=i+1))

@user_passes_test(User_Check, login_url="/")
def Welcome(request):
	print("Username: " + request.user.username)
	_User = request.user
	_Member = Member.objects.get(User=_User)
	_Level = _Member.Level
	print("Level: " + str(_Member.Level))
	print("Squat: " + str(_Member.Squat))
	context = {}

	if request.GET.get("Create_Program"):
		print("Creating Program")
		print("Start Date: " + str(request.GET.get("Start_Date")))
		Start_Date_String = request.GET.get("Start_Date")
		Day_1_String = request.GET.get("Day_1")
		Day_2_String = request.GET.get("Day_2")
		Day_3_String = request.GET.get("Day_3")
		Day_4_String = request.GET.get("Day_4")
		# print("Day 1: " + str(request.GET.get("Day_1")))
		# print("Day 2: " + str(request.GET.get("Day_2")))
		# print("Day 3: " + str(request.GET.get("Day_3")))
		# print("Day 4: " + str(request.GET.get("Day_4")))
		Start_Date_List = Start_Date_String.split("-")
		Start_Year = int(Start_Date_List[0])
		Start_Month = int(Start_Date_List[1])
		Start_Date = int(Start_Date_List[2])
		Start_Datetime = datetime.strptime(Start_Date_String, "%Y-%m-%d")
		Days_List = [int(Day_1_String), int(Day_2_String), int(Day_3_String), int(Day_4_String)]
		# print("Start Year: " + str(Start_Year))
		# print("Start Month: " + str(Start_Month))
		# print("Start Date: " + str(Start_Date))
		# print("Days: " + str(Days_List))
		print(Days_List)
		print(Start_Datetime)

		Generate_Workouts(Start_Datetime, _Level, Days_List, _Member)
		# return HttpResponseRedirect("/welcome")
		_Member.New = False
		_Member.Has_Workout = True
		_Member.save()
		return HttpResponseRedirect("/userpage")
		# Generate_Workouts(datetime(Year, Month, Day), _Level, [Day_1, Day_2, Day_3])
	return render(request, "welcome.html", context)
