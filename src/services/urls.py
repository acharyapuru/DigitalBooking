from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('<slug:slug>/', views.ServiceDetail.as_view(), name='service_detail'),
]
