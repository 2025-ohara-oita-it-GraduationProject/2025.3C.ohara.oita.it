from django import forms
from .models import CustomUser,TeacherProfile,StudentProfile

class SignupForm(forms.ModelForm):
    username = forms.CharField(label='ログイン', max_length=100)
    password = forms.CharField(label='ログインパスワード',widget=forms.PasswordInput)
    teacher_name = forms.CharField(label='名前',max_length=100)
    teacher_password = forms.CharField(label='教師パス',widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password1','teacher_name','teacher_password']  # teacher_password は除外

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
                teacher_name=self.cleaned_data['teacher_name'],
                teacher_password=self.cleaned_data['teacher_password']
            )
        return user

class StudentLoginForm(forms.Form):
    username = forms.CharField(
        label='ID',
        widget=forms.TextInput(attrs={'placeholder': 'ID'})
    )
    password = forms.CharField(
        label='パス',
        widget=forms.PasswordInput(attrs={'placeholder': 'パス'})
    )