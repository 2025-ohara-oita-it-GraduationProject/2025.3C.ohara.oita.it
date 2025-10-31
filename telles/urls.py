from django.urls import path
from . import views

app_name = 'telles'

urlpatterns = [
    path('', views.index, name='index'),  # トップページ
    path('student/create/', views.student_create, name='student_create'),
    path('attendance/', views.attendance_list, name='attendance_list'),  # 出欠簿ページ
    path('logout/', views.logout_view, name='logout'),  # ログアウト処理
    path('login/', views.login_view, name='login'), 
]