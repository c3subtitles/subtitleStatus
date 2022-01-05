# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
import django.contrib.auth


def index(request):
    pass


def login(request):
    if request.user.is_authenticated():
        redirect('/')
    if request.method == 'POST':
        username = request.POST['accountName']
        password = request.POST['accountPassword']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            django.contrib.auth.login(request, user)
            if "next" in request.POST:
                return redirect(request.POST['next'])
    next = "/"
    if "next" in request.GET:
        next = request.GET['next']
    return render(request, 'login.html', {"next": next})


def logout(request):
    django.contrib.auth.logout(request)
    return redirect('/')
