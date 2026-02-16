from django.db import models
from django.contrib.auth.models import AbstractUser
import unicodedata
from django.utils import timezone

# ===============================
# カスタムユーザーモデル
# ===============================
class CustomUser(AbstractUser):
    # 教師か生徒かを識別
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    
    # メールアドレスと認証状態
    email = models.EmailField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

from django.db import models

# ================================
# クラス登録モデル
# ================================
class ClassRegistration(models.Model):
    department = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.department}"


# ===============================
# 教師データベース
# ===============================
class TeacherProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    teacher_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teacher_database'  # 教師専用テーブル名

    def __str__(self):
        return f"{self.teacher_name} (user_id={self.user.id}, username={self.user.username})"


# ===============================
# 生徒データベース
# ===============================
class StudentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_name = models.CharField(max_length=30)
    student_number = models.IntegerField()
    created_by_teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # 追加
    department = models.ForeignKey(
        ClassRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name = 'students'
    )
    
    academic_year = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    
    COURSE_YEARS_CHOICES = [
        (1, '1年制'),
        (2, '2年制'),
        (3, '3年制'),
    ]
    course_years = models.IntegerField(
        choices = COURSE_YEARS_CHOICES,
        null=True,
        blank=True,
        db_index=True
    )
    class Meta:
        db_table = 'student_database'  # 生徒専用テーブル名
        ordering = ['student_number']
        
    def __str__(self):
        return f"{self.student_number}: {self.student_name}"
    
    
class Attendance(models.Model):

    STATUS_CHOICES = [
        ('absent', '欠席'),
        ('late', '遅刻'),
        ('leave', '早退'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    time = models.DateTimeField(default=timezone.now)


    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True)
    checked = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.student_number} - {self.date} - {self.status}"


class AttendanceLog(models.Model):
    """
    出席連絡の履歴を保存するモデル
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_logs')
    date = models.DateField(db_index=True)
    time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Attendance.STATUS_CHOICES)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-time']  # 新しい順

    def __str__(self):
        return f"{self.student.student_name} - {self.date} ({self.time}) - {self.status}"


# ===============================
# メール認証コード
# ===============================
class EmailVerificationCode(models.Model):
    """
    メール認証用の一時コードを保存するモデル
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)  # 6桁の数字
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # 有効期限（10分後）
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.code} (expires: {self.expires_at})"
    
    def is_valid(self):
        """コードが有効かどうかを判定"""
        return not self.is_used and timezone.now() < self.expires_at


# ===============================
# 信頼済みデバイス
# ===============================
class TrustedDevice(models.Model):
    """
    信頼済みデバイスを管理するモデル（3ヶ月間有効）
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trusted_devices')
    device_token = models.CharField(max_length=64, unique=True, db_index=True)  # ランダムトークン
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # 有効期限（3ヶ月後）
    last_used = models.DateTimeField(auto_now=True)
    user_agent = models.TextField(blank=True)  # ブラウザ情報（参考用）
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_token[:8]}... (expires: {self.expires_at})"
    
    def is_valid(self):
        """デバイストークンが有効かどうかを判定"""
        return timezone.now() < self.expires_at



