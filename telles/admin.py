from django.contrib import admin
from .models import CustomUser, TeacherProfile, StudentProfile, Attendance, ClassRegistration, AttendanceLog, EmailVerificationCode, TrustedDevice

# ===============================
# カスタムユーザーモデルを管理画面に表示
# ===============================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'email_verified', 'is_teacher', 'is_student', 'is_superuser')
    list_filter = ('is_teacher', 'is_student', 'is_superuser', 'email_verified')
    search_fields = ('username', 'email')


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

# ===============================
# メール認証コードを管理画面に表示
# ===============================
@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'code')
    ordering = ('-created_at',)

# ===============================
# 信頼済みデバイスを管理画面に表示
# ===============================
@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_token_short', 'created_at', 'expires_at', 'last_used')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__username', 'device_token')
    ordering = ('-created_at',)
    
    def device_token_short(self, obj):
        """トークンの最初の8文字のみ表示"""
        return f"{obj.device_token[:8]}..."
    device_token_short.short_description = 'Device Token'