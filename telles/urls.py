from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'telles'  # 名前空間を統一

urlpatterns = [
    path('', views.index_view, name='index'),  # ← トップページをホーム画面に変更
    path('teacher_signup/', views.teacher_signup_view, name='teacher_signup'),
    path('teacher_login/', views.teacher_login_view, name='teacher_login'),
    path('student_signup/', views.student_signup_view, name='student_signup'),
    path('student_login/', views.student_login_view, name='student_login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
