from django.urls import path
from . import views

app_name = 'telles'

urlpatterns = [
<<<<<<< HEAD
    path('', views.IndexView.as_view(), name='index'),
    path('signup/', views.signup_view, name='signup'),
=======
    path('', views.index, name='index'),  # トップページ
    path('student/create/', views.student_create, name='student_create'),
    path('attendance/', views.attendance_list, name='attendance_list'),  # 出欠簿ページ
    path('logout/', views.logout_view, name='logout'),  # ログアウト処理
    path('login/', views.login_view, name='login'), 
>>>>>>> 3bd8a2b20f3323807832c8df2ebbbdeb5f84293b
]