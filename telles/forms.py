from django import forms
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CustomUser, TeacherProfile, StudentProfile, ClassRegistration

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
    course_years = forms.IntegerField(required=False)
    student_id = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    number = forms.IntegerField()
    fullname = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        self.selected_departments = kwargs.pop('course_departments', None)
        self.selected_academic_years = kwargs.pop('selected_academic_years', None)
        self.selected_course_years = kwargs.pop('selected_course_years', None)
        self.selected_department = kwargs.pop('selected_department', None)  # ← 追加
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        departments = self.data.getlist("department[]")
        for i, dept in enumerate(departments):
            if not dept:
                self.add_error(f"department", "学科を選択してください。")
                break
        return cleaned_data

    def save_all(self, request):
        academic_years = request.POST.getlist("academic_year[]")
        departments = request.POST.getlist("department[]")
        course_years_list = request.POST.getlist("course_years[]")
        student_ids = request.POST.getlist("student_id[]")
        passwords = request.POST.getlist("password[]")
        numbers = request.POST.getlist("number[]")
        fullnames = request.POST.getlist("fullname[]")

        users = []
        
        # ▼ 配列の数を確認（student_ids を含める）
        total = len(student_ids)
        
        # 各リストの長さが total と一致しない場合は空行を補完して合わせる
        def pad_list(lst):
            if len(lst) < total:
                lst += [''] * (total - len(lst))
            return lst

        academic_years = pad_list(academic_years)
        departments = pad_list(departments)
        course_years_list = pad_list(course_years_list)
        passwords = pad_list(passwords)
        numbers = pad_list(numbers)
        fullnames = pad_list(fullnames)

        for i in range(total):
            sid = student_ids[i].strip()
            if not sid:
                continue

            if not sid.isdigit():
                messages.error(request, f"ID: {sid} は半角数字で入力してください。")
                continue

            dept = departments[i].strip()
            if not dept:
                messages.error(request, f"{sid} の学科が選択されていません。")
                continue

            try:
                with transaction.atomic():
                    if CustomUser.objects.filter(username=sid).exists():
                        messages.warning(request, f"{sid} はすでに登録されています。")
                        continue

                    user = CustomUser.objects.create_user(
                        username=sid,
                        password=passwords[i],
                        is_student=True,
                        is_teacher=False
                    )

                    try:
                        department_obj = ClassRegistration.objects.get(department=dept)
                    except ClassRegistration.DoesNotExist:
                        messages.error(request, f"{sid} の学科 {dept} は存在しません。")
                        raise ValueError("Department not found")

                    academic_year = (self.selected_academic_years if self.selected_academic_years else academic_years[i])
                    course_years = (self.selected_course_years if self.selected_course_years else course_years_list[i])

                    StudentProfile.objects.create(
                        user=user,
                        student_name=fullnames[i],
                        student_number=int(numbers[i]) if numbers[i] else None,
                        academic_year=academic_year,
                        department=department_obj,
                        course_years=int(course_years) if course_years is not None else None,
                        created_by_teacher=self.teacher
                    )
                    users.append(user)

            except Exception as e:
                if str(e) != "Department not found":
                    messages.error(request, f"{sid} の登録中にエラーが発生しました: {e}")
                continue

        if not users:
            messages.error(request, "登録できる生徒がいませんでした。入力を確認してください。")

        return users
    
class ClassRegistrationForm(forms.ModelForm):

    class Meta:
        model = ClassRegistration
        fields = ['department',]
        widgets = {
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例：情報IT三年制学科',
            }),
        }
        labels = {
            'department': '学科名',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].error_messages = {
            'required': '学科名を入力してください。',
            'unique': 'この学科名は既に登録されています。'
        }

    def clean_department(self):
        department = self.cleaned_data.get('department')
        if ClassRegistration.objects.filter(department=department).exists():
             raise forms.ValidationError("この学科名は既に登録されています。")
        return department

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
            if not student_number.isdigit():
                raise forms.ValidationError("IDは半角数字で入力してください。")

            try:
                user = CustomUser.objects.get(student_profile__student_number=student_number)
            except (CustomUser.DoesNotExist, ValueError):
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

class StudentProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 必須に設定
        self.fields['department'].required = True
        self.fields['academic_year'].required = True
        self.fields['course_years'].required = True
        
        # カスタムエラーメッセージ
        self.fields['department'].error_messages = {'required': '学科を選択してください。'}
        self.fields['academic_year'].error_messages = {'required': '年度を入力してください。'}
        self.fields['course_years'].error_messages = {'required': '年制を選択してください。'}

    def clean_academic_year(self):
        academic_year = self.cleaned_data.get('academic_year')
        if academic_year:
            if not academic_year.isascii() or not academic_year.isdigit():
                raise forms.ValidationError("年度は半角数字で入力してください。")
            if len(academic_year) != 4:
                raise forms.ValidationError("年度は4桁で入力してください。")
        return academic_year

    class Meta:
        model = StudentProfile
        fields = ['student_name', 'student_number', 'department', 'academic_year', 'course_years']
        labels = {
            'student_name': '名前',
            'student_number': '番号',
            'department': '学科',
            'academic_year': '年度',
            'course_years': '年制',
        }
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'course_years': forms.Select(attrs={'class': 'form-control'}),
        }
 