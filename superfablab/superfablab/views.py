from django.shortcuts import render, redirect
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def profile(request):
    return coming_soon(request)


def coming_soon(request):
    return render(request, 'coming_soon.html')