from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.contrib.auth import logout

    
def index(request):
    return render(request, 'index.html', {'username': request.user.username})

def student_create(request):
    return render(request, 'student_create.html')

def attendance_list(request):
    return render(request, 'attendance_list.html', {'username': request.user.username})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('telles:index')
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('telles:login')