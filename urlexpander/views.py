from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.utils import timezone
import datetime
from memento_client import MementoClient
import requests
from bs4 import BeautifulSoup
from .models import URL
from .forms import SearchForm
from urllib import request as urllibreq
import json
import boto3
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from urlexpander.models import URL
from urlexpander.serializers import URLSerializer

# For phahtomjs cloud
api_key = "ak-53wg4-aq5mb-cahrf-t8s7s-ymzkq"

# Creates URL table and handles new URL creation
@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def url_list(request):
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			new_url = form.save(commit = False)
			new_url.date = timezone.now()
			# Runs when URL is correct
			try:
				response = requests.get(new_url)
				page = BeautifulSoup(response.content, "lxml")
				if page.title is not None:
					title = page.title.string
				else:
					title = "No Title Available"
				new_url.status = response.status_code
				new_url.final_url = response.url
				new_url.title = title
				# Wayback storing
				current_date = datetime.datetime.now()
				memento = MementoClient()
				wayback_res = memento.get_memento_info(response.url, current_date).get("mementos").get("closest")
				new_url.wayback = wayback_res.get("uri")[0]
				if wayback_res.get("datetime") is not None:
					new_url.wayback_date = str(wayback_res.get("datetime"))
				else:
					new_url.wayback_date = str(current_date)
				# Picture archiving
				# Connecting to S3
				s3_connection = boto3.resource("s3")
				# For image capture with PhahtomJS
				data = json.dumps({"url":response.url, "renderType":"jpeg"}).encode("utf-8")
				headers = {"content-type": "application/json"}
				api_url = "http://PhantomJScloud.com/api/browser/v2/" + api_key + "/"
				req = urllibreq.Request(url=api_url, data=data, headers=headers)
				res = urllibreq.urlopen(req)
				result = res.read()
				# Puts the generated image on S3
				s3_connection.Bucket("lab3pics").put_object(Key=str(current_date) + ".jpg", Body=result, ACL="public-read", ContentType="image/jpeg")
				# Generates a publicly accessible link to the image
				pic_url = "http://s3.amazonaws.com/lab3pics/" + str(current_date) + ".jpg"
				new_url.archive_link = pic_url
			# Sets up error message
			except Exception as e:
				new_url.status = "None"
				new_url.final_url = "Does not exist"
				new_url.title = "This webpage does not exist"
				new_url.wayback = "Not available"
				new_url.wayback_date = "Not available"
				new_url.archive_link = e
				# Redirects to details page
			finally:
				new_url.save()
				return redirect('url_detail', pk = new_url.pk)
	else:
		urls = URL.objects.filter(date__lte = timezone.now()).order_by('-date')
		form = SearchForm
	return render(request, 'urlexpander/url_list.html', {'urls': urls, 'form': SearchForm})

# Sends information for the "Detail" page
@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def url_detail(request, pk):
	url = get_object_or_404(URL, pk = pk)
	return render(request, 'urlexpander/url_detail.html', {'url': url})

# Handles the deletion of a URL from the list
@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def delete_url(request, pk):
	url = get_object_or_404(URL, pk = pk)
	url_key = url.archive_link
	# Connection to S3 Bucket for pic storage	
	boto3.session.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
	s3_connection = boto3.client("s3")
	# Check to see if the img exists in the bucket
	exists = False
	try:
		s3_connection.get_object(Bucket="lab3pics", Key=url_key)
	except:
		exists = False
	finally:
		if exists is not False:
			exists = True
	# If the img exists within the bucket, delete it from S3
	if exists is True:
		s3_connection.delete_object(Bucket="lab3pics", Key=url_key)
	# Remove the URL data from the database
	url.delete()
	return	HttpResponseRedirect('../')

# Handles logging a user out
def logout_url(request):
	logout(request)
	return redirect('login')

# API Logic

# GET a list of all current URLs or POST a new URL
@api_view(["GET", "POST"])
@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def list_urls(request, format=None):
	if request.method == "GET":
		urls = URL.objects.all()
		serializer = URLSerializer(urls, many = True)
		return Response(serializer.data)
	elif request.method == "POST":
		serializer = URLSerializer(data = request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status = status.HTTP_201_CREATED)
	else:
		return Response(status = status.HTTP_400_BAD_REQUEST)

# GET a specific URL or DELETE a specific URL
@api_view(["GET", "DELETE"])
@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def detail_url(request, pk, format=None):
	try:
		url = URL.objects.get(pk = pk)
	except URL.DoesNotExist:
		return Response(status = status.HTTP_404_NOT_FOUND)
	if request.method == "GET":
		serializer = URLSerializer(url, many = True)
		return Response(serializer.data)
	elif request.method == "DELETE":
		url.delete()
		return Response(status = status.HTTP_204_NO_CONTENT)
	else:
		return Response(status = status.HTTP_400_BAD_REQUEST)
