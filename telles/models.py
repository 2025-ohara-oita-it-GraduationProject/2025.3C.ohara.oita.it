from django.db import models
from django.contrib.auth.models import AbstractUser

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
    student_number = models.IntegerField(unique=True)
    created_by_teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_database'  # 生徒専用テーブル名

    def __str__(self):
        return f"{self.student_name} (user_id={self.user.id}, username={self.user.username})"