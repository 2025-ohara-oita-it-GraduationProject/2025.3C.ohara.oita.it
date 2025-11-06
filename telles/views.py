from django.shortcuts import render, redirect
<<<<<<< HEAD
from django.contrib.auth import login
from django.views.generic.base import TemplateView
from .forms import SignupForm
# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'
    
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            teacher_password = form.cleaned_data.get('teacher_password')

            # 教師判定
            if teacher_password == "teachpass123":
                user.is_staff = True

            user.save()
            login(request, user)
            return redirect('/')  # または redirect('index')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})
=======
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
>>>>>>> 3bd8a2b20f3323807832c8df2ebbbdeb5f84293b
