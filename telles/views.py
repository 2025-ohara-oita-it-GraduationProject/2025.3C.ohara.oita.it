from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from .models import CustomUser, TeacherProfile, StudentProfile
from .forms import TeacherSignupForm, StudentSignupForm, TeacherLoginForm, StudentLoginForm
from django.http import HttpResponse
from django.utils import timezone
from .models import Attendance
from datetime import datetime, date


# トップページ
def index_view(request):
    return render(request, 'index.html')

#ログイン選択
def login_selection_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'teacher':
            return redirect('telles:teacher_login')
        elif user_type == 'student':
            return redirect('telles:student_login')
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

# 生徒サインアップ（単体 or 一括登録対応可能）
def student_signup_view(request):
    teacher = getattr(request.user, 'teacher_profile',None)
    if not teacher:
        messages.error(request, "教師としてログインしてください")
        return redirect('telless:teacher_login')
    
    if request.method == 'POST':
        ids = request.POST.getlist('id[]')
        passwords = request.POST.getlist('password[]')
        names = request.POST.getlist('fullname[]')
        numbers = request.POST.getlist('number[]')
        classrooms = request.POST.getlist('classroom[]')
        
        success_count = 0
        for i in range(len(ids)):
            if ids[i].strip() and passwords[i].strip() and names[i].strip() and classrooms[i].strip():
                user = CustomUser(username=ids[i], is_student=True,is_teacher=False)
                user.set_password(passwords[i])
                user.save()
                
                StudentProfile.objects.create(
                    user=user,
                    student_name=names[i],
                    student_number=int(numbers[i]),
                    class_name = classrooms[i],
                    created_by_teacher=teacher
                )
                success_count += 1
                
        if success_count > 0:
            messages.success(request,f"{success_count}名の生徒アカウントを登録しました。")
            return redirect('telles:index')
        else:
            messages.error(request, "登録に失敗しました。")
    return render(request, 'student_signup.html')


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
                return redirect('telles:stu_calendar')
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
    date = request.GET.get("date")

    students = StudentProfile.objects.all()

    return render(request, "class_list.html", {
        "students": students,
        "date": date,   # ← これを渡す
    })

# 詳細ページ
from django.shortcuts import get_object_or_404
from .models import StudentProfile, Attendance

def detail(request, student_id, date_str):
    student = get_object_or_404(StudentProfile, id=student_id)

    attendance = Attendance.objects.filter(
        student=student,
        date=date_str
    ).first()

    return render(request, "detail.html", {
        "student": student,
        "attendance": attendance,
        "date": date_str,
    })


# カレンダー
def calendar_view(request):
    return render(request, 'calendar.html')

def stu_calendar_view(request):
    return render(request, 'stu_calendar.html')
# views.py
STATUS_JP = {
    "absent": "欠席",
    "late": "遅刻",
    "leaveearly": "早退"
}
 


def attendance_form(request):
    STATUS_JP = {
        "absent": "欠席",
        "late": "遅刻",
        "leaveearly": "早退"
    }

    if request.method == "POST":
        action = request.POST.get("action")
        status = request.POST.get("status")
        reason = request.POST.get("reason")
        date_str = request.GET.get("date", None)  # ここは文字列のまま取得

        # 日付を YYYY-MM-DD に変換
        try:
            date = datetime.strptime(date_str, "%Y年%m月%d日").date() if date_str else None
        except ValueError:
            messages.error(request, "日付形式が正しくありません。")
            return redirect("attendance_form")  # または適切な戻り先

        # 確認 → 確認ページへ
        if action == "confirm":
            status_jp = STATUS_JP.get(status, status)
            return render(request, "attendance_confirm.html", {
                "status": status_jp,
                "reason": reason,
                "date": date,
                "status_val": status  # ← hidden に渡す用
            })

        # 送信 → DB 保存
        elif action == "send":
            student = request.user.student_profile

            Attendance.objects.update_or_create(
                student=student,
                date=date,  # ここに変換済み日付を渡す
                defaults={
                    "status": status,
                    "reason": reason
                }
            )

            return render(request, "attendance_done.html", {
                "date": date,
                "status": STATUS_JP.get(status, status),
                "reason": reason
            })

        # 戻る
        elif action == "back":
            return redirect(f'/stu_calendar/?date={date_str}')  # 戻りは元の文字列のままでもOK

    return render(request, "attendance_form.html")
 
def submit_attendance(request):
    if request.method == "POST":
        date = request.POST.get("date")
        status = request.POST.get("status")
        reason = request.POST.get("reason")
        # ここでDB保存などの処理を行う
        return HttpResponse(f"{date} の {status} 理由: {reason} を受け付けました！")
    return redirect('telles:stu_calendar')

def attendance_detail(request, date_str):
    # URL から日付文字列を受け取る場合
    # 例: date_str = '2025-11-19'
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    student = request.user.student_profile

    # 指定日付のAttendanceだけを取得
    attendance = Attendance.objects.filter(student=student, date=date).first()

    return render(request, "detail.html", {
        "attendance": attendance,
        "date": date
    })