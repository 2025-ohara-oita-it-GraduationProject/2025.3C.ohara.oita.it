from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    teacher_password = forms.CharField(
        label='教師パスワード',
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': '教師パスワード（教師のみ）'})
    )

    class Meta:
        model = User
        fields = ['username', 'password1']  # teacher_password は除外
        labels = {
            'username': 'ID',
            'password1': 'パス',
        }

    # 確認用パスワードを使わないようにオーバーライド
    password2 = None

class StudentLoginForm(forms.Form):
    username = forms.CharField(
        label='ID',
        widget=forms.TextInput(attrs={'placeholder': 'ID'})
    )
    password = forms.CharField(
        label='パス',
        widget=forms.PasswordInput(attrs={'placeholder': 'パス'})
    )