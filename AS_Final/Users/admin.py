from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from django.db import models
import datetime
from django.contrib.auth.models import User, Group
from django.contrib import admin
from .models import Workout, Set, Exercise, Member, SubWorkout, Workout_Template, Workout

class MemberAdmin(admin.ModelAdmin):
	pass

class ExerciseAdmin(admin.ModelAdmin):
	pass

class SubWorkoutAdmin(admin.ModelAdmin):
	pass

class SetAdmin(admin.ModelAdmin):
	pass

class Workout_TemplateAdmin(admin.ModelAdmin):
	pass

class WorkoutAdmin(admin.ModelAdmin):
	pass

# Register your models here.
admin.site.register(Member, MemberAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(SubWorkout, SubWorkoutAdmin)
admin.site.register(Set, SetAdmin)
admin.site.register(Workout_Template, Workout_TemplateAdmin)
admin.site.register(Workout, WorkoutAdmin)
