from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.generic.base import TemplateView

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'

def index(request):
    return render(request, 'index.html')

def attendance(request):
    return render(request, 'attendance.html')

def logout_view(request):
    logout(request)  # Djangoのセッションを終了
    return redirect('login')  # ログイン画面にリダイレクト

