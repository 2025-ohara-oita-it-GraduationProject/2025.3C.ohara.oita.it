from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, TeacherProfile, StudentProfile


# ===============================
# 教師サインアップフォーム
# ===============================
class TeacherSignupForm(forms.ModelForm):
    """
    教師が自分のアカウントを作成するフォーム。
    CustomUser と TeacherProfile の両方を作成。
    """
    username = forms.CharField(label='ログインID', max_length=100)
    password = forms.CharField(label='ログインパスワード', widget=forms.PasswordInput)
    teacher_name = forms.CharField(label='名前', max_length=100)
    
    class Meta:
        model = CustomUser
        fields = ['username','password','teacher_name']

    def save(self, commit=True):
        user = CustomUser(
            username=self.cleaned_data['username'],
            is_teacher=True,
            is_student=False
        )
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            TeacherProfile.objects.create(
                user=user,
                teacher_name=self.cleaned_data['teacher_name']
            )

        return user


# ===============================
# 生徒サインアップフォーム（教師が作成）
# ===============================
class StudentSignupForm(forms.ModelForm):
    username = forms.CharField(label='生徒ID', max_length=150)
    password = forms.CharField(label='初期パスワード', widget=forms.PasswordInput)
    student_name = forms.CharField(label='名前', max_length=100)
    student_number = forms.IntegerField(label='番号')

    class Meta:
        model = StudentProfile
        fields = ['student_name', 'student_number']

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = CustomUser(
            username=self.cleaned_data['username'],
            is_teacher=False,
            is_student=True
        )
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            StudentProfile.objects.create(
                user=user,
                student_name=self.cleaned_data['student_name'],
                student_number=self.cleaned_data['student_number'],
                created_by_teacher=self.teacher
            )
        return user


# ===============================
# 教師ログインフォーム
# ===============================
class TeacherLoginForm(forms.Form):
    username = forms.CharField(label='ID', max_length=150)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)


# ===============================
# 生徒ログインフォーム（既存）
# ===============================
class StudentLoginForm(forms.Form):
    username = forms.CharField(label='ID', max_length=150)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)


# ===============================
# 新規追加：サインアップ共通（UserCreationForm版）
# ===============================
class SignupForm(UserCreationForm):
    teacher_password = forms.CharField(
        label='教師パスワード',
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': '教師パスワード（教師のみ）'})
    )

    class Meta:
        model = User
        fields = ['username', 'password1']
        labels = {
            'username': 'ID',
            'password1': 'パス',
        }

    # 確認用パスワードを使わない
    password2 = None


# ===============================
# 新規追加：生徒ログインフォーム（UIつき）
# ===============================
class StudentLoginFormV2(forms.Form):
    username = forms.CharField(
        label='ID',
        widget=forms.TextInput(attrs={'placeholder': 'ID'})
    )
    password = forms.CharField(
        label='パス',
        widget=forms.PasswordInput(attrs={'placeholder': 'パス'})
    )
