from django.urls import path

from . import views

urlpatterns = [
    path('converter/', views.index, name='converter_home'),
]
