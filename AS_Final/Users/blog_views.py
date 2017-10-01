# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout, login, authenticate
from django.core.files import File
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
from .forms import BlogPostForm
import json
import stripe     
import re


def Blog(request): 

	form = BlogPostForm()
	return render(request, 'blog.html', {'form': form})
