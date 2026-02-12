from django.contrib import admin
from .models import CustomUser, TeacherProfile, StudentProfile, Attendance,ClassRegistration

# ===============================
# カスタムユーザーモデルを管理画面に表示
# ===============================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'is_teacher', 'is_student', 'is_superuser')
    list_filter = ('is_teacher', 'is_student', 'is_superuser')
    search_fields = ('username',)


# ===============================
# 教師プロフィールを管理画面に表示
# ===============================
@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher_name', 'user', 'created_at')
    search_fields = ('teacher_name', 'user__username')


# ===============================
# 生徒プロフィールを管理画面に表示
# ===============================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_name', 'student_number','academic_year','department','course_years','created_by_teacher','user','created_at',)
    search_fields = ('student_name','student_number','user__username',)
    list_filter = ('academic_year','department','course_years','created_by_teacher',)
    ordering = ('student_number',)

# ===============================
# 出欠データを管理画面に表示

#クラス登録管理
@admin.register(ClassRegistration)
class ClassRegistrationAdmin(admin.ModelAdmin):
    list_display = ('department',)
    search_fields = ('department',)
    ordering = ('department',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'reason')
    list_filter = ('status', 'date')
    search_fields = ('student__student_name', 'reason')

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'time', 'status', 'reason')
    list_filter = ('status', 'date', 'time')
    search_fields = ('student__student_name', 'reason')