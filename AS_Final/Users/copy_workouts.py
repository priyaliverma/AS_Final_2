from Users.models import Workout_Template, SubWorkout

def Copy_Workouts():
	f = open("Workouts.txt", "w+")
	f.write("Subworkout Format: Order,Type,Sets,Reps,Deload,Alloy_Reps,Stop,Drop,RPE")
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
			Sub_String += str(S.Strength_Drop) + ","
			Sub_String += str(S.RPE)
			Workout_String += Sub_String
		Workout_String += "\n"
		f.write(Workout_String)
	f.close()
