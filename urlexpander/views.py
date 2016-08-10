from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.utils import timezone
import requests
from bs4 import BeautifulSoup
from .models import URL
from .forms import SearchForm

# Creates URL table and handles new URL creation
@login_required(login_url="/accounts/login/")
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
			# Sets up error message
			except Exception as e:
				new_url.status = "None"
				new_url.final_url = "Does not exist"
				new_url.title = "This webpage does not exist"
				pass
			# Redirects to details page
			finally:
				new_url.save()
				return redirect('url_detail', pk = new_url.pk)
	else:
		urls = URL.objects.filter(date__lte = timezone.now()).order_by('-date')
		form = SearchForm
	return render(request, 'urlexpander/url_list.html', {'urls': urls, 'form': SearchForm})

# Sends information for the "Detail" page
@login_required(login_url="/accounts/login/")
def url_detail(request, pk):
	url = get_object_or_404(URL, pk = pk)
	return render(request, 'urlexpander/url_detail.html', {'url': url})

# Handles the deletion of a URL from the list
@login_required(login_url="/accounts/login/")
def delete_url(request, pk):
	url = get_object_or_404(URL, pk = pk)
	url.delete()
	return	HttpResponseRedirect('../')

def logout_url(request):
	logout(request)
	return redirect('login')
