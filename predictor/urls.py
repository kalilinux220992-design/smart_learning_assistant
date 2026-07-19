from django.urls import path

from predictor import views

app_name = "predictor"

urlpatterns = [
    path("", views.home, name="home"),
    path("predict/", views.predict, name="predict"),
    path("students/", views.students, name="students"),
    path("companies/", views.companies, name="companies"),
    path("algorithms/", views.algorithms, name="algorithms"),
    path("home/", views.home, name="home-legacy"),
]
