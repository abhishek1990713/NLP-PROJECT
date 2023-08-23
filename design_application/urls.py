from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.index,name ='homes'),
    path("detect-object/", views.detect_objects, name='detect_objects'),
    path('run_app/',views.run_app, name="run_app")
]