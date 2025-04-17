from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views import View
from .models import Service

# Create your views here.
class ServiceDetail(View):
    def get(self, request, slug):
        service = get_object_or_404(Service, slug=slug)

        if service.service_type == 'Movies':
            return redirect('movie:movies')
        else:
            return redirect('index')
