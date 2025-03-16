from django.contrib import admin
from django.urls import path, include
from home import views
from .views import custom_logout , admin_dashboard 


urlpatterns = [
    path("", views.home, name='home'),
    path("upload/", views.upload, name='upload'),
    path("login/", views.login_view, name='login'),  # Updated function name
    path("view_data/", views.view_data, name='view_data'),
    path("register/", views.register, name='register'),
    path("main/", views.main, name="main"),
    path("train/", views.train, name="train"),
    path("predict/", views.predict, name="predict"),
    path('logout/', custom_logout, name='logout'),
     path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
]
