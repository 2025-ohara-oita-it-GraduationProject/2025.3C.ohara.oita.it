from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# ===============================
# カスタムユーザーモデル
# ===============================
class CustomUser(AbstractUser):
    # 教師か生徒かを識別
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    def __str__(self):
        return self.username

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
    student_name = models.CharField(max_length=100)
    student_number = models.IntegerField()
    class_name = models.CharField(max_length=50)
    created_by_teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # 追加
    department = models.CharField(max_length=100, blank=True, null=True)
    academic_year = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'student_database'  # 生徒専用テーブル名
        ordering = ['class_name','student_number']

    def __str__(self):
        return f"{self.class_name}-{self.student_name}: {self.student_name}"
    
    
class Attendance(models.Model):

    STATUS_CHOICES = [
        ('absent', '欠席'),
        ('late', '遅刻'),
        ('leave', '早退'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.DateTimeField(default=timezone.now)


    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True)
    checked = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.student_number} - {self.date} - {self.status}"



# ================================
# クラス登録モデル
# ================================
class ClassRegistration(models.Model):
    department = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('department', 'class_name')
        
    def __str__(self):
        return f"{self.department}{self.class_name}"
