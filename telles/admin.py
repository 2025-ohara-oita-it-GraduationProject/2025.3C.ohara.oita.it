from django.contrib import admin
from .models import CustomUser, TeacherProfile, StudentProfile


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
    list_display = ('id', 'student_name', 'student_number', 'created_by_teacher', 'user', 'created_at')
    search_fields = ('student_name', 'user__username')
    list_filter = ('created_by_teacher',)
