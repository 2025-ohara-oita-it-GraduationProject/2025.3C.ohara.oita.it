from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from .models import CustomUser, TeacherProfile, StudentProfile
from .forms import TeacherSignupForm, StudentSignupForm, TeacherLoginForm, StudentLoginForm
from .models import Student

# トップページ
def index_view(request):
    return render(request, 'index.html')

#ログイン選択
def login_selection_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'teacher':
            return redirect('telless:teacher_login')
        elif user_type == 'student':
            return redirect('telless:student_login')
        else:
            return render(request, 'login_selection.html',{'error': '選択してください'})
    else:
        return render(request, 'login_selection.html')
    
# 教師サインアップ
def teacher_signup_view(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        teacher_code = request.POST.get('teacher_code', '').strip()
        
        if not teacher_code or teacher_code != getattr(settings, 'TEACHER_COMMON_PASSWORD', None):
            messages.error(request, "教師パスワードがありません")
            return render(request, 'teacher_signup.html', {
                'form':form, 
                'teacher_code_error':"教師パスが正しくありません。"
            })
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            teacher_name = form.cleaned_data['teacher_name']
            
            user = CustomUser.objects.create_user(
                username = username,
                password = password
            )
            user.is_teacher = True
            user.save()
            
            TeacherProfile.objects.create(
                user=user,
                teacher_name = teacher_name
            )
            
            messages.success(request, "教師アカウントを登録しました。")
            return redirect('telles:teacher_login')
        else:
            messages.error(request, "登録に失敗しました。")
            print(form.errors)
    else:
        form = TeacherSignupForm()
    return render(request, 'teacher_signup.html', {'form': form})

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

# 生徒ログイン
def student_login_view(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_student:
                login(request, user)
                messages.success(request, f"{user.student_profile.student_name}さん、ログインしました。")
                return redirect('telles:index')
            else:
                messages.error(request, "IDまたはパスが違います。")
    else:
        form = StudentLoginForm()
    return render(request, 'student_login.html', {'form': form})

# 生徒登録ページ
def student_create(request):
    return render(request, 'student_create.html')

# 出欠簿
def attendance_list(request):
    return render(request, 'attendance_list.html', {'username': request.user.username})

# クラス一覧（個別ページ）
def class_list(request):
    students = Student.objects.all()
    return render(request, "class_list.html", {"students": students})

# 詳細ページ
def detail(request):
    return render(request, 'detail.html')

# カレンダー
def calendar_view(request):
    return render(request, 'calendar.html')
