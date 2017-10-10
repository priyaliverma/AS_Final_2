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
from Shared_Functions import *

Days_Of_Week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

Exercise_Types = ["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat", "LB Uni Push",
"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2"]

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

def Create_Test_Users():
	Test_1, created = User.objects.get_or_create(username="Test_1")
	if created:
		user.set_password("Test_1")
		user.save()
		_Member = Member.objects.create(User = Test_1)
		_Member.save()

	Test_2, created = User.objects.get_or_create(username="Test_2")
	if created:
		user.set_password("Test_2")
		user.save()
		_Member = Member.objects.create(User = Test_2)
		_Member.Paid = True
		_Member.Expiry_Date = datetime.now() + datetime.timedelta(days=3)
		_Member.save()

	Test_3, created = User.objects.get_or_create(username="Test_3")
	if created:
		user.set_password("Test_3")
		user.save()
		_Member = Member.objects.create(User = Test_3)
		_Member.Paid = True
		_Member.Expiry_Date = datetime.now() + datetime.timedelta(days=3)
		_Member.Read = True
		_Member.save()

	Test_4, created = User.objects.get_or_create(username="Test_4")
	if created:
		user.set_password("Test_4")
		user.save()
		_Member = Member.objects.create(User = Test_4)
		_Member.Paid = True
		_Member.Expiry_Date = datetime.now() + datetime.timedelta(days=3)
		_Member.Read = True
		_Member.Agreed = True
		_Member.save()

	Expired, created = User.objects.get_or_create(username="Expired")
	if created:
		user.set_password("Expired")
		user.save()
		_Member = Member.objects.create(User = Expired)
		_Member.Paid = True
		_Member.Read = True
		_Member.Agreed = True
		_Member.Expiry_Date = datetime.now() - datetime.timedelta(days=3)
		_Member.save()
	return None


def Home(request):
	context = {}
	Current_User = request.user

	Lift_Names = ["Squat", "Bench", "Deadlift", "Overhead_Press", "Power_Clean", "C_Jerk", "Snatch"]
	context["Login_Failed"] = ""
	context["Signup_Error"] = ""
	Lifts = {}
	Lifts_In_Pounds = {}
	RPE_Experience = False
	# print("User: " + str(request.user))
	# print("USername: " + request.user.username)
	# for i in User.objects.all():
	# 	print("Existing username: " + i.username)

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
			print("LOGIN FAILED")
			print("User not authenticated")
			context["Login_Failed"] = "Login Failed - Please Try Again"
		return render(request, "homepage_abridged.html", context)


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
		Weight_lbs = request.GET.get("Weight_lbs")
		Weight_kg = request.GET.get("Weight_kgs")
		Squat = request.GET["Squat_lbs_Input"]
		RPE_Exp = request.GET["RPE_Exp_Input"]

		if (F_Name != "" and L_Name != "" and Email != "" and P_Word_1 != "" and P_Word_1 == P_Word_2):
			print(F_Name)
			print(L_Name)
			print(Email)
			print(P_Word_1)
			print(P_Word_2)
			print(DOB)
			print(Weight_lbs)
			print(Squat)
			print(RPE_Exp)
			if User.objects.filter(username = Email).exists():
				context["Signup_Error"] = "An account with that email has already been created!"
				print("Sign-up Error")
				return render(request, "homepage_abridged.html", context)
			else:
				print("Signing Up...")
				New_User = User.objects.create_user(Email, password=P_Word_1)
				New_User.first_name = F_Name
				New_User.last_name = L_Name
				# User(first_name = F_Name, last_name = L_Name, email= Email, username = Email, password = P_Word_1)
				New_User.save()
				Body_Weight = int(Weight_lbs)
				if Squat != "":
					Squat_Weight = int(Squat)
				else:
					Squat_Weight = 0
				if RPE_Exp == "yes":
					RPE_Experience = True
				else:
					RPE_Experience = False
				Assigned_Level = 1
				if Squat_Weight < Body_Weight:
					Assigned_Level = 1
				elif Squat_Weight > Body_Weight*1.5 and Bench_Weight > Body_Weight and RPE_Experience:
					Assigned_Level = 11
				else:
					Assigned_Level = 6
				New_Member = Member(User = New_User, Level = Assigned_Level, Squat = Squat_Weight)
				# Creating Member
				New_Member.New = True
				New_Member.DOB = DOB
				# New_Member.Height = Member_Height
				Body_Weight = int(Weight_lbs)
				New_Member.Weight = Body_Weight
				New_Member.Squat = Squat_Weight
				New_Member.save()

				user = authenticate(username=Email, password=P_Word_1)
				if user is not None:
				    	login(request, user)
				# return HttpResponseRedirect("/terms-conditions")
				# return HttpResponseRedirect("/waiver")
				return HttpResponseRedirect("/sign-up-confirmation")
	return render(request, "homepage_abridged.html", context)

@user_passes_test(Member_Exists, login_url="/")
# @user_passes_test(New_Check, login_url="/")
def SignUp_Confirmation(request):
	context = {}
	User = request.user
	_Member = Member.objects.get(User=User)
# 	stripe.api_key = "sk_test_KTmWLzrdvb6Zt6K0SLOD22Zk"
	# LIVE!!
	stripe.api_key = "sk_live_rDFsGbC9IPjseHT9GhF0xDic"

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

	# for i in stripe.Customer.all():
	# 	print("Stripe Customer: " + str(i.id))

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
			context["Total"] = '{:.2f}'.format((i[2] + Processing_Fee))
			context["End_Date"] = (datetime.now() + i[3]).date()
			Subscription_Time = i[3]
			# print(datetime.now())
			# print(datetime.now() + i[3])
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
			_Member.New = False
			_Member.Signup_Date = datetime.now()
			_Member.Expiry_Date = datetime.now() + Subscription_Time
			_Member.save()
			print(_Member.Signup_Date)
			print(_Member.Expiry_Date)
			# print("New Customer Charged! " + str(_ID) + " Amount: " + str(charge.amount))
			return HttpResponseRedirect("/waiver")

		except stripe.error.CardError:
			print("Card Error - PAYMENT DECLINED")
			context["Payment_Status"] = "Payment Failed!"
			return render(request, "signup_confirmation.html", context)

	if request.GET.get("Payment_btn"):
		print("Payment Button Pressed")
		return HttpResponseRedirect("/Welcome")
	return render(request, "signup_confirmation.html", context)

# @user_passes_test(Tier_2, login_url="/")
@user_passes_test(Member_Exists, login_url="/")
@user_passes_test(Member_Paid, login_url="/sign-up-confirmation/")
@user_passes_test(Not_Agreed, login_url="/")
def Waiver(request):
	context = {}
	User = request.user
	_Member = Member.objects.get(User=User)
	if "Empty_Input" in request.session.keys():
		context["Empty"] = "Please enter today's date, name and indicate agreement before continuing!"
	if request.POST.get("Agree"):
		print(request.POST.keys())
		if request.POST["full_name"] != "" and request.POST["date"] != "" and "agree_check" in request.POST.keys():
			Start_Date_String = request.POST["date"]
			Start_Datetime = datetime.strptime(Start_Date_String, "%Y-%m-%d")
			if Start_Datetime.date() != datetime.now().date():
				context["Error"] = "Please enter the correct date!"
				return render(request, "waiver.html", context)
			else:
				_Member.Agreed = True
				_Member.save()
				return HttpResponseRedirect("/terms-conditions")
		else:
			context["Error"] = "Please enter today's date, name and indicate agreement before continuing!"
			request.session["Empty_Input"] = True
		# print(request.POST["agree_check"])
	return render(request, "waiver.html", context)

@user_passes_test(Member_Exists, login_url="/")
@user_passes_test(Member_Paid, login_url="/sign-up-confirmation/")
@user_passes_test(Member_Agreed, login_url="/waiver/")
@user_passes_test(Not_Read, login_url="/")
def Terms_Conditions(request):
	context = {}
	User = request.user
	_Member = Member.objects.get(User=User)
	if request.POST.get("Continue"):
		_Member.Read = True
		_Member.save()
		return HttpResponseRedirect("/welcome")
	return render(request, "terms_conditions.html", context)

@user_passes_test(Member_Exists, login_url="/")
@user_passes_test(Member_Paid, login_url="/sign-up-confirmation/")
@user_passes_test(Member_Agreed, login_url="/waiver/")
@user_passes_test(Member_Read, login_url="/terms-conditions/")
@user_passes_test(No_Workouts, login_url="/")
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

		if Day_1_String == "" or Day_1_String == None or Day_2_String == "" or Day_2_String == None or Day_3_String == "" or Day_3_String == None or Day_4_String == "" or Day_4_String == None:
			context["Error"] = "Please choose 4 different workout days!"
			return render(request, "welcome.html", context)

		Start_Date_List = Start_Date_String.split("-")
		Start_Year = int(Start_Date_List[0])
		Start_Month = int(Start_Date_List[1])
		Start_Date = int(Start_Date_List[2])
		Start_Datetime = datetime.strptime(Start_Date_String, "%Y-%m-%d")
		if Start_Datetime.date() < datetime.now().date():
			context["Error"] = "Invalid start date. Please choose a start date that is not in the past"
			return render(request, "welcome.html", context)
		Days_List = [int(Day_1_String), int(Day_2_String), int(Day_3_String), int(Day_4_String)]

		Generate_Workouts(Start_Datetime, _Level, Days_List, _Member)
		# return HttpResponseRedirect("/welcome")
		_Member.New = False
		_Member.Has_Workouts = True
		_Member.save()
		return HttpResponseRedirect("/userpage")
		# Generate_Workouts(datetime(Year, Month, Day), _Level, [Day_1, Day_2, Day_3])
	return render(request, "welcome.html", context)


@user_passes_test(Inside_Access, login_url="/")
def Membership_Expired(request):
	context = {}
	User = request.user
	_Member = Member.objects.get(User=User)
# 	stripe.api_key = "sk_test_LKsnEFYm74fwmLbyfR3qKWgb"
	# LIVE!!
	stripe.api_key = "sk_live_rDFsGbC9IPjseHT9GhF0xDic"
	Package_Description = "Gold"
	print("RPE Test: " + str(Get_Weight(200, 8, 8)))

	Packages = [["Gold ($300.00)", "G", 300.00, timedelta(days=365)], ["Silver ($180.00)", "S", 180.00, timedelta(days=180)],
	["Bronze ($40.00)", "B", 40.00, timedelta(days=30)]]
	request.session["Package"] = "G"
	context["Packages"] = []

	Processing_Fee = 0
	context["Processing_Fee"] = Processing_Fee

	Extension_Start = datetime.now()

	if _Member.Expiry_Date != None and _Member.Expiry_Date.date() >= datetime.now().date():
		Extension_Start = _Member.Expiry_Date
		context["Message"] = "Your current membership lasts until: "
		context["Expiry_Date"] = _Member.Expiry_Date.date()
		context["Message_2"] = " Choose one of the packages below to extend your membership"
	else:
		context["Message"] = "Your membership has expired!"
		context["Message_2"] = "Choose one of the packages below to renew your membership"
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
			Total = round(i[2] + Processing_Fee, 2)*100
			# Total = "{0:.2f}".format(i[2] + Processing_Fee)
			context["Total"] = '{:.2f}'.format((i[2] + Processing_Fee))
			context["End_Date"] = (Extension_Start + i[3]).date()
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
			if _Member.Expiry_Date != None and _Member.Expiry_Date.date() >= datetime.now().date():
				_Member.Expiry_Date = _Member.Expiry_Date + Subscription_Time
				_Member.save()
			else:
				_Member.Expiry_Date = datetime.now() + Subscription_Time
				_Member.save()
			print(_Member.Signup_Date)
			print(_Member.Expiry_Date)
			# print("New Customer Charged! " + str(_ID) + " Amount: " + str(charge.amount))
			return HttpResponseRedirect("/userpage")

		except stripe.error.CardError:
			print("Card Error - PAYMENT DECLINED")
			context["Payment_Status"] = "Payment Failed!"
			return render(request, "member_expired.html", context)

	if request.GET.get("Payment_btn"):
		print("Payment Button Pressed")
		return HttpResponseRedirect("/welcome")
	return render(request, "member_expired.html", context)

