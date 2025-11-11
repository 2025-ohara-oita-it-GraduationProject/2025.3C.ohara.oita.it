from django import forms
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
    teacher_password = forms.CharField(label='教師パス', widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ['username','password','teacher_name','teacher_password']  # ログイン用IDのみフォームに表示

    def save(self, commit=True):
        # ① CustomUser（ログイン情報）を作成
        user = CustomUser(
            username=self.cleaned_data['username'],
            is_teacher=True,
            is_student=False
        )
        user.set_password(self.cleaned_data['password'])  # ログイン用パスをハッシュ化

        if commit:
            user.save()

            # ② TeacherProfile（教師情報）を作成
            TeacherProfile.objects.create(
                user=user,
                teacher_name=self.cleaned_data['teacher_name'],
                teacher_password=self.cleaned_data['teacher_password']  # 教師用パスを平文保存
            )
        return user


# ===============================
# 生徒サインアップフォーム（教師が作成）
# ===============================
class StudentSignupForm(forms.ModelForm):
    """
    教師が生徒アカウントを一括で作成するフォーム。
    """
    username = forms.CharField(label='生徒ID', max_length=150)
    password = forms.CharField(label='初期パスワード', widget=forms.PasswordInput)
    student_name = forms.CharField(label='名前', max_length=100)
    student_number = forms.IntegerField(label='番号')

    class Meta:
        model = StudentProfile
        fields = ['student_name', 'student_number']

    def __init__(self, *args, **kwargs):
        # ログイン中の教師情報を受け取る
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # ① CustomUser（ログイン情報）を作成
        user = CustomUser(
            username=self.cleaned_data['username'],
            is_teacher=False,
            is_student=True
        )
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            # ② StudentProfile（生徒情報）を作成
            StudentProfile.objects.create(
                user=user,
                student_name=self.cleaned_data['student_name'],
                student_number=self.cleaned_data['student_number'],
                created_by_teacher=self.teacher  # 登録した教師を紐づけ
            )
        return user


# ===============================
# 教師ログインフォーム
# ===============================
class TeacherLoginForm(forms.Form):
    """
    教師専用ログインフォーム。
    """
    username = forms.CharField(label='ID', max_length=150)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)


# ===============================
# 生徒ログインフォーム
# ===============================
class StudentLoginForm(forms.Form):
    """
    生徒専用ログインフォーム。
    """
    username = forms.CharField(label='ID', max_length=150)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)
