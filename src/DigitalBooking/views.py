from django.shortcuts import render
from services.models import Service
from offer.models import PromoCode

# Create your views here.
def index(request):
    search_query = request.GET.get('q', '')
    if search_query:
        services = Service.objects.filter(name__icontains=search_query)
        context = {
            "services": services
        }

    else:
        services = Service.objects.all()
        notices = PromoCode.objects.filter(conditions__validity__is_active=True) or None
        context = {
            "services": services,
            "notices": notices
        }
    return render(request, 'index.html', context)

def login(request):
    return render(request, 'login.html')