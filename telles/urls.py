from django.urls import path
from . import views

app_name = 'telles'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('signup/', views.signup_view, name='signup'),
]