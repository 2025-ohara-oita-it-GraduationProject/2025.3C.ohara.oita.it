from django import forms
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, TeacherProfile, StudentProfile,ClassRegistration
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib import messages


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
# 生徒サインアップフォーム（教師が一括登録）
# ===============================
class StudentSignupForm(forms.Form):
    """
    複数生徒を一括登録するフォーム（配列で受け取る）
    """
    academic_year = forms.CharField(required=False)
    department = forms.CharField(required=False)
    classroom = forms.CharField(required=False)
    student_id = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    number = forms.IntegerField()
    fullname = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("department"):
            self.add_error("department", "学科を選択してください。")

        if not cleaned_data.get("classroom"):
            self.add_error("classroom", "クラスを選択してください。")

    def save_all(self, request):
        academic_years = request.POST.getlist("academic_year[]")
        departments = request.POST.getlist("department[]")
        classrooms = request.POST.getlist("classroom[]")
        student_ids = request.POST.getlist("student_id[]")
        passwords = request.POST.getlist("password[]")
        numbers = request.POST.getlist("number[]")
        fullnames = request.POST.getlist("fullname[]")

        users = []
        
        # ▼ 配列の数を確認（student_ids を含める）
        total = len(student_ids)
        if not all(len(lst) == total for lst in [
            academic_years, departments, classrooms,
            student_ids, passwords, numbers, fullnames
        ]):
            messages.error(request, "すべてのフィールドが一致していません。入力を確認してください。")
            return[]

        for i in range(total):
            if CustomUser.objects.filter(username=student_ids[i]).exists():
                messages.warning(request, f"{student_ids[i]}はすでに登録されています。")
                continue
            try:
                user = CustomUser.objects.create_user(
                    username=student_ids[i],
                    password=passwords[i],
                )

                StudentProfile.objects.create(
                    user=user,
                    student_name=fullnames[i],
                    student_number=numbers[i],
                    academic_year=academic_years[i],
                    department=departments[i],
                    class_name=classrooms[i],
                    created_by_teacher=self.teacher
                )

                users.append(user)
            
            except IntegrityError:
                messages.error(request, f"{student_ids[i]}の登録中にエラーが発生しました。")
                continue

        return users
    
class ClassRegistrationForm(forms.ModelForm):

    class Meta:
        model = ClassRegistration
        fields = ['department', 'class_name']
        widgets = {
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例：情報IT三年制学科',
            }),
            'class_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例：1-A',
            }),
        }
        labels = {
            'department': '学科名',
            'class_name': 'クラス名',
        }

    def clean_name(self):
        cleaned = super().clean()
        department = cleaned.get('department')
        class_name = cleaned.get('class_name')


        if department and class_name:
            if ClassRegistration.objects.filter(
                department=department,
                class_name=class_name
                ).exists():
                    raise forms.ValidationError("この学科とクラス名の組み合わせは既に登録されています。")

        return cleaned  

# ===============================
# 教師ログインフォーム
# ===============================
class TeacherLoginForm(forms.Form):
    username = forms.CharField(label='ID', max_length=150)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            # ユーザー認証
            user = authenticate(username=username, password=password)

            if user is None:
                # IDが存在するか確認
                from .models import CustomUser
                if not CustomUser.objects.filter(username=username).exists():
                    raise ValidationError("入力されたIDは存在しません。")
                else:
                    raise ValidationError("パスワードが正しくありません。")

        return cleaned_data

# ===============================
# 生徒ログインフォーム（既存）
# ===============================
class StudentLoginForm(forms.Form):
    student_number = forms.CharField(label='ID', max_length=150)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        student_number = cleaned_data.get("student_number")
        password = cleaned_data.get("password")

        if student_number and password:
            try:
                user = CustomUser.objects.get(student_profile__student_number=student_number)
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("IDまたはパスワードが正しくありません。")

            if not user.check_password(password):
                raise forms.ValidationError("IDまたはパスワードが正しくありません。")

            self.user = user

        return cleaned_data

    def get_user(self):
        return self.user


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
