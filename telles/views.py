from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import CustomUser, TeacherProfile
from .forms import TeacherSignupForm, TeacherLoginForm

# トップページ
def index_view(request):
    return render(request, 'index.html')

# 教師サインアップ
def teacher_signup_view(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            teacher_name = form.cleaned_data['teacher_name']
            teacher_pass = form.cleaned_data['teacher_password']
            
            user = CustomUser.objects.create_user(
                username=username,
                password=password
            )
            user.is_teacher = True
            user.save()
            
            TeacherProfile.objects.create(
                user=user,
                teacher_name=teacher_name,
                teacher_password=teacher_pass
            )
            
            messages.success(request, "教師アカウントを登録しました。")
            return redirect('telles:teacher_login')
        else:
            messages.error(request, "登録に失敗しました。")
            print(form.errors)
    else:
        form = TeacherSignupForm()
    return render(request, 'signup.html', {'form': form})

# 教師ログイン
def teacher_login_view(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_teacher:
                login(request, user)
                messages.success(request, f"{user.teacher_profile.teacher_name}さん、ログインしました。")
                return redirect('telles:index')
            else:
                messages.error(request, "IDまたはパスが違います。")
    else:
        form = TeacherLoginForm()
    return render(request, 'login.html', {'form': form})
