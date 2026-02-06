from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from .models import CustomUser, TeacherProfile, StudentProfile
from .forms import TeacherSignupForm, StudentSignupForm, TeacherLoginForm, StudentLoginForm,ClassRegistrationForm
from django.http import HttpResponse, JsonResponse
from .models import Attendance
from datetime import datetime, date
from django.utils import timezone

# トップページ
def index_view(request):
    selected_year = request.session.get("selected_year")
    selected_major = request.session.get("selected_class")  # ← 学科 (修正: selected_major -> selected_class)
    selected_course = request.session.get("selected_course")

    students = StudentProfile.objects.select_related('user', 'department').all()

    if selected_year:
        students = students.filter(academic_year=selected_year)
    if selected_major:
        students = students.filter(department__department=selected_major)
    if selected_course:
        students = students.filter(course_years=selected_course)

    # 出席情報
    today_date = date.today()
    attendance_map = {a.student_id: a for a in Attendance.objects.filter(date=today_date)}
    for s in students:
        s.attendance = attendance_map.get(s.id)

    # 未確認通知
    attendances = Attendance.objects.filter(date=today_date, checked=False)
    notify_map = {att.student_id: att for att in attendances}

    return render(request, "index.html", {
        "students": students,
        "year": selected_year,
        "major": selected_major,
        "attendance_map": attendance_map,
        "notify_map": notify_map,
        "date": today_date,
    })

 
 
 
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
           

            return redirect('telles:teacher_login')
        else:

            print(form.errors)
    else:
        form = TeacherSignupForm()
    return render(request, 'teacher_signup.html', {'form': form})

# 生徒サインアップ（単体 or 一括登録対応可能）
from .models import ClassRegistration

def student_signup_view(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        messages.error(request, "教師としてログインしてください")
        return redirect('telles:teacher_login')

    class_list = ClassRegistration.objects.all()

    selected_academic_years = request.session.get('selected_year')
    selected_course_years = request.session.get('selected_course')
    selected_department = request.session.get('selected_class')

    # テンプレート用に選択フラグを付与
    for c in class_list:
        c.is_selected = (c.department == selected_department)

    course_years_list = [
        {'value': '1', 'name': '1年制', 'is_selected': (selected_course_years == '1')},
        {'value': '2', 'name': '2年制', 'is_selected': (selected_course_years == '2')},
        {'value': '3', 'name': '3年制', 'is_selected': (selected_course_years == '3')},
    ]

    is_year_only = (selected_academic_years and not selected_department and not selected_course_years)
    
    form_kwargs = {
        "teacher": teacher,
        "selected_academic_years": None if is_year_only else selected_academic_years,
        "selected_course_years": None if is_year_only else selected_course_years,
        "selected_department": None if is_year_only else selected_department,
        
    }


    if request.method == 'POST':
        form = StudentSignupForm(request.POST, **form_kwargs)
        users = form.save_all(request)

        if users:
            count = len(users)
            return render(request, 'student_complete.html', {
                'registered_count': count
            })

        return render(request, 'student_signup.html',{
            'form':form,
            'class_list':class_list,
            'course_years_list': course_years_list,
            'selected_academic_year': selected_academic_years,
            'is_year_only': is_year_only,   # ★ テンプレ用
        })

    form = StudentSignupForm(**form_kwargs)
    return render(request, 'student_signup.html', {
        'form': form,
        'class_list': class_list,
        'course_years_list': course_years_list,
        'selected_academic_year': selected_academic_years,
        'is_year_only': is_year_only,
    })
 
 
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
                return redirect('telles:class_select')
            else:
                messages.error(request, "IDまたはパスが違います。")
    else:
        form = TeacherLoginForm()
    return render(request, 'login.html', {'form': form})
 
# 生徒ログイン（student_number で user を取得して直接ログイン）
def student_login_view(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            password = form.cleaned_data['password']

            # 数値チェック
            if not student_number.isdigit():
                form.add_error('student_number', "IDは数字で入力してください。")
                return render(request, 'student_login.html', {'form': form})

            try:
                user = CustomUser.objects.get(student_profile__student_number=student_number)
            except (CustomUser.DoesNotExist, ValueError):
                # ユーザーが見つからない、または予期せぬエラー
                form.add_error(None, "学生番号またはパスワードが違います。")
                return render(request, 'student_login.html', {'form': form})
 
            if user.check_password(password):
                login(request, user)
                # 正しいリダイレクト
                return redirect('telles:student_index')
            else:
                messages.error(request, "学生番号またはパスワードが違います。")
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
 
    # 今日の日付（またはGET指定日）
    date_str = request.GET.get("date")
    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        target_date = datetime.today().date()
 
    # クラスの生徒一覧（例として全員）
    students = StudentProfile.objects.all()
 
    # その日で未確認の申請を取得
    attendances = Attendance.objects.filter(
        date=target_date,
        checked=False
    )
   
    selected_year = request.session.get("selected_year")
    selected_class = request.session.get("selected_class")
    selected_course = request.session.get("selected_course") # 追記: 年制を取得

    # 年度・クラスで絞り込み
    if selected_year and selected_class:
        students = students.filter(academic_year=selected_year, department__department=selected_class)

    # 追記: 年制があれば絞り込み
    if selected_course:
        students = students.filter(course_years=selected_course)
   
    #==============================
    attendance_map = {a.student_id: a for a in Attendance.objects.filter(date=target_date)}
 
    for s in students:
        s.attendance = attendance_map.get(s.id)
    #==============================
 
    # { student_id: Attendance } みたいに辞書化
    notify_map = {att.student_id: att for att in attendances}
 
    return render(request, "class_list.html", {
        "students": students,
        "date": target_date,
        "notify_map": notify_map,   # 🔥 通知が来てる生徒が分かる
       
    #==============================
        "attendance_map": attendance_map
    #==============================
       
       
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
   
    previous_url = request.META.get('HTTP_REFERER', '/class_list/')
 
    if attendance and not attendance.checked:
        attendance.checked = True
        attendance.save()
 
    return render(request, "detail.html", {
        "student": student,
        "attendance": attendance,
        "date": date_str,
        "previous_url": previous_url
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

        # 戻る
        if action == "back":
            return redirect(f'/stu_calendar/?date={date_str}')

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
            local_time = timezone.localtime(timezone.now())
            attendance_obj, created = Attendance.objects.update_or_create(
                student=student,
                date=date,  # ここに変換済み日付を渡す
                defaults={
                    "status": status,
                    "reason": reason,
                    "checked": False,
                    "time":local_time
                }
            )
 
            return render(request, "attendance_done.html", {
                "date": date,
                "status": STATUS_JP.get(status, status),
                "reason": reason,
                "time": attendance_obj.time,
            })
 
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
   
#クラス選択
def class_select_view(request):
    if not request.user.is_authenticated or not request.user.is_teacher:
        return redirect('telles:teacher_login')
 
    errors = []
    selected_year = ''
    selected_class = ''
    selected_course = ''
 
    if request.method == "POST":
        selected_year = request.POST.get("year")
        selected_class = request.POST.get("department")
        selected_course = request.POST.get("course_years")
 
        if not selected_year:
            errors.append("年度とクラスを選択してください。")
        else:
            request.session["selected_year"] = selected_year
            request.session["selected_class"] = selected_class
            request.session["selected_course"] = selected_course
            return redirect('telles:index')

    current_year = datetime.now().year
    # DB に登録されている年度を取得（NULL/空は除外）
    db_years = (
        StudentProfile.objects
        .exclude(academic_year__isnull=True)
        .exclude(academic_year__exact='')
        .values_list("academic_year", flat=True)
        .distinct()
    )

    # set で統合（重複排除）
    year_set = set(str(y) for y in db_years)
    year_set.add(str(current_year))  # ★ 今年は必ず入れる (文字列として追加)

    # ソート（降順：今年 → 過去）
    years = sorted(year_set, reverse=True)


    classes = (
        ClassRegistration.objects
        .values_list("department", flat=True)
        .distinct()
        .order_by("department")
    )
 
    return render(request, "class_select.html", {
        "years": years,
        "classes": classes,
        "errors": errors,
        "selected_year": selected_year,
        "selected_class": selected_class,
        "selected_course": selected_course,
    })
 
   
from .forms import StudentProfileUpdateForm
 
def profile_view(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
   
    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            # messages.success(request, "プロフィールを更新しました。")  # ユーザー要望により非表示
            return redirect('telles:profile', student_id=student.id)
    else:
        form = StudentProfileUpdateForm(instance=student)
 
    return render(request, "profile.html", {
        "student": student,
        "form": form
    })
 
def student_account_view(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        messages.error(request, "生徒としてログインしてください。")
        return redirect("telles:student_login")
 
    return render(request, "student_account.html")
 
# 生徒用：自分のパスワードを変更する
def student_reset_password_view(request):
    # 生徒ログイン済みかチェック
    student = getattr(request.user, "student_profile", None)
    if not student:
        messages.error(request, "生徒としてログインしてください。")
        return redirect("telles:student_login")
 
    if request.method == "POST":
        storage = messages.get_messages(request)
        for _ in storage:
            pass
 
        new_password = request.POST.get("new_password")
        new_password2 = request.POST.get("new_password2")
 
        # 未入力チェック
        if not new_password or not new_password2:
            messages.error(request, "パスワードを入力してください。")
            return redirect("telles:student_reset_password")
 
        # 一致チェック
        if new_password != new_password2:
            messages.error(request, "パスワードが一致しません。")
            return redirect("telles:student_reset_password")
 
        # パスワード更新
        user = request.user
        user.set_password(new_password)
        user.save()
 
        # ★完了画面を表示
        return render(request, "student_reset_password_done.html")
 
    return render(request, "student_reset_password.html")
 
#クラス登録画面
def class_signup_view(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    
    if not teacher:
        messages.error(request, "教師としてログインしてください")
        return redirect('telles:teacher_login')
    
    if request.method == 'POST':
        form = ClassRegistrationForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            
            form.save()
            
            return render(request, 'class_complete.html',{
                'department':department,
            })
        else:
            messages.error(request, "登録できませんでした。内容を確認してください。")
    else:
        form = ClassRegistrationForm()
        
    return render(request, 'class_signup.html', {
        'form': form
    })
 
def student_index_view(request):
    if not request.user.is_authenticated or request.user.is_teacher:
        messages.error(request, "生徒としてログインしてください。")
        return redirect('telles:student_login')
    
    student = request.user.student_profile
    today_date = date.today()
    
    # 出席情報（今日のものがあれば取得）
    attendance = Attendance.objects.filter(student=student, date=today_date).first()
    
    return render(request, "student_index.html", {
        "student": student,
        "attendance": attendance,
        "date": today_date,
    })

def stu_calender_view(request):
    return render(request, 'stu_calender.html')
 
 
 
def class_list_view(request):
    # 教師ログイン必須
    if not request.user.is_authenticated or not request.user.is_teacher:
        return redirect('telles:teacher_login')
 
    # 選択された年度・クラスを session から取得
    selected_year = request.session.get("selected_year")
    selected_class = request.session.get("selected_class")
 
    # 今日の日付（またはGET指定日）
    date_str = request.GET.get("date")
    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        target_date = datetime.today().date()
 
    # 選択されたクラスの生徒のみ取得
    if selected_year and selected_class:
        students = StudentProfile.objects.select_related('user', 'department').filter(
            academic_year=selected_year,
            department__department=selected_class.strip()  # 空白を除去
        ).order_by("student_number")
        
        selected_course = request.session.get("selected_course")
        if selected_course:
            students = students.filter(course_years=selected_course)
        students = students.order_by("student_number")
    else:
        students = StudentProfile.objects.none()  # クラス未選択の場合は空
 
    # 出席情報を添付
    attendance_map = {a.student_id: a for a in Attendance.objects.filter(date=target_date)}
    for s in students:
        s.attendance = attendance_map.get(s.id)
 
    # 未確認通知
    attendances = Attendance.objects.filter(date=target_date, checked=False)
    notify_map = {att.student_id: att for att in attendances}
 
    return render(request, "class_list.html", {
        "students": students,
        "date": target_date,
        "notify_map": notify_map,
        "attendance_map": attendance_map,
        "selected_year": selected_year,
        "selected_class": selected_class,
    })
 
 
def class_list_api(request):
    """
    出欠簿データをJSON形式で返すAPI
    教員側のリアルタイム更新用
    """
    # 教師ログイン必須
    if not request.user.is_authenticated or not request.user.is_teacher:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # セッションから選択情報を取得
    selected_year = request.session.get("selected_year")
    selected_class = request.session.get("selected_class")
    
    # 日付取得
    date_str = request.GET.get("date")
    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        target_date = datetime.today().date()
    
    # 生徒データ取得
    if selected_year and selected_class:
        students = StudentProfile.objects.select_related('user', 'department').filter(
            academic_year=selected_year,
            department__department=selected_class.strip()
        )
        
        selected_course = request.session.get("selected_course")
        if selected_course:
            students = students.filter(course_years=selected_course)
        students = students.order_by("student_number")
    else:
        students = StudentProfile.objects.none()
    
    # 出席情報を取得
    attendance_map = {a.student_id: a for a in Attendance.objects.filter(date=target_date)}
    
    # 未確認通知
    attendances = Attendance.objects.filter(date=target_date, checked=False)
    notify_map = {att.student_id: att for att in attendances}
    
    # JSONデータ作成
    students_data = []
    for student in students:
        attendance = attendance_map.get(student.id)
        students_data.append({
            'id': student.id,
            'student_number': student.student_number,
            'student_name': student.student_name,
            'is_active': student.user.is_active,
            'has_notification': student.id in notify_map,
            'attendance': {
                'status': attendance.status if attendance else None,
                'status_display': attendance.get_status_display() if attendance else '出席',
            } if student.user.is_active else None
        })
    
    return JsonResponse({
        'students': students_data,
        'date': target_date.strftime('%Y-%m-%d')
    })
 

 
# 生徒削除（退学処理）
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
 
def teacher_required(user):
    return user.is_authenticated and user.is_teacher
 
@login_required
@user_passes_test(teacher_required)
def student_delete_view(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    if request.method == 'POST':
        # ★ 物理削除しない
        user = student.user
        user.is_active = False
        user.save()   # ← ここが超重要

        return redirect('telles:delete_complete', action='expel')

    # GETアクセス時はプロフィールページに戻す
    return redirect('telles:profile_view', student_id=student.id)


@login_required
@user_passes_test(teacher_required)
def student_hard_delete_view(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)

    if request.method == 'POST':
        student_name = student.student_name

        # CustomUser と 1対1 の場合は user を消すのが安全
        student.user.delete()
        # ↑ CASCADE で StudentProfile も消える

        return redirect('telles:delete_complete', action='delete')

    return redirect('telles:profile', student_id=student.id)

def student_restore_view(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)

    if request.method == "POST":
        user = student.user
        user.is_active = True
        user.save()

        messages.success(
            request,
            f"{student.student_name} さんを復学しました。"
        )
        return redirect('telles:delete_complete', action='restore')

    return redirect("telles:index")

@login_required
@user_passes_test(teacher_required)
def delete_complete_view(request, action):
    context = {
        'title': '完了',
        'message': '処理が正常に完了しました。'
    }
    if action == 'delete':
        context['title'] = '削除完了'
        context['message'] = '生徒の情報が完全に削除されました。'
    elif action == 'expel':
        context['title'] = '退学完了'
        context['message'] = '生徒の退学処理が完了しました。'
    elif action == 'restore':
        context['title'] = '復学完了'
        context['message'] = '生徒の復学処理が完了しました。'
        
    return render(request, 'delete_complete.html', context)

def logout_complete_view(request):
    return render(request, 'logout_complete.html')
from django.db.models import Count, Q

def attendance_summary(request):
    """
    学科・クラスごとの出欠集計を表示するビュー。
    """
    target_date_str = request.GET.get("date")
    if target_date_str:
        try:
            target_date = date.fromisoformat(target_date_str)
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    selected_year = request.session.get("selected_year")
    selected_course = request.session.get("selected_course")

    # 1. フィルタ条件に合致する全生徒を取得
    students_qs = StudentProfile.objects.select_related('user', 'department')
    
    # 学年フィルタ
    if selected_year:
        students_qs = students_qs.filter(academic_year=selected_year)
    # コースフィルタ（1年制/2年制など）集計には反映しないように変更
    # if selected_course:
    #     students_qs = students_qs.filter(course_years=selected_course)

    # 2. 指定日の出欠情報を取得
    attendance_qs = Attendance.objects.filter(date=target_date)
    att_map = {a.student_id: a.status for a in attendance_qs}

    # 3. 集計用マップの初期化（全学科を網羅）
    # 学科ID -> データの辞書
    summary_map = {}
    for dept in ClassRegistration.objects.all():
        summary_map[dept.id] = {
            "class_name": dept.department,
            "total": 0, "present": 0, "absent": 0, "late": 0, "leave": 0
        }
    
    # 「未所属」枠
    unassigned_key = "unassigned"
    summary_map[unassigned_key] = {
        "class_name": "未所属",
        "total": 0, "present": 0, "absent": 0, "late": 0, "leave": 0
    }

    # 4. 生徒一人ずつカウント
    for s in students_qs:
        # 退学者は集計に含めない（または含める場合はここで調整）
        # トップページが全表示なのでここでも全表示が望ましい可能性あり
        # 今回は is_active=True の現役学生のみを集計対象とする
        if not s.user.is_active:
            continue

        key = s.department_id if s.department_id else unassigned_key
        # 万が一、モデルにない学科IDが残っている場合のセーフティ
        if key not in summary_map and key != unassigned_key:
            key = unassigned_key

        status = att_map.get(s.id)
        
        summary_map[key]["total"] += 1
        if status == "absent":
            summary_map[key]["absent"] += 1
        elif status == "late":
            summary_map[key]["late"] += 1
        elif status == "leave":
            summary_map[key]["leave"] += 1
        else:
            # 欠席・遅刻・早退の記録がない場合は「出席（または未入力）」
            summary_map[key]["present"] += 1

    # 5. リスト化して出席率を計算
    summary = []
    # 学科名順にソート（必要なら）
    for key, data in summary_map.items():
        total = data["total"]
        # 在籍0人の学科は表示しない（未所属も0人なら隠す）
        if total > 0:
            data["rate"] = round((data["present"] / total) * 100, 1) if total > 0 else 0
            summary.append(data)
        elif key != unassigned_key:
            # 学科として登録されているものは0人でも表示する（仕様による）
            data["rate"] = 0
            summary.append(data)

    # 6. 全体合計の計算
    total_students = sum(item["total"] for item in summary)
    total_absent = sum(item["absent"] for item in summary)
    total_late = sum(item["late"] for item in summary)
    total_leave = sum(item["leave"] for item in summary)
    total_present = sum(item["present"] for item in summary)
    
    total_summary = {
        "total": total_students,
        "present": total_present,
        "absent": total_absent,
        "late": total_late,
        "leave": total_leave,
        "rate": round((total_present / total_students) * 100, 1) if total_students > 0 else 0
    }

    return render(request, "attendance_summary.html", {
        "date": target_date,
        "summary": summary,
        "total_summary": total_summary,
    })
