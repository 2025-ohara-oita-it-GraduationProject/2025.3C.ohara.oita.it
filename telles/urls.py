from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'telles'  # 名前空間を統一

urlpatterns = [
    path('', views.login_selection_view, name='login_selection'),
    path('index/', views.index_view, name='index'),  # ← トップページをホーム画面に変更
    path('teacher_signup/', views.teacher_signup_view, name='teacher_signup'),
    path('teacher_login/', views.teacher_login_view, name='teacher_login'),
    path('student_signup/', views.student_signup_view, name='student_signup'),
    path('student_login/', views.student_login_view, name='student_login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('student/create/', views.student_create, name='student_create'),
    path('class_list/', views.class_list, name='class_list'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('class_select/', views.class_select_view, name='class_select'),
    path('classroom/',views.ClassRoomview, name="classroom"),
    path("student/<int:student_id>/restore/",views.student_restore_view,name="student_restore"),
    
    # 詳細・カレンダー
    path('detail/<int:student_id>/<str:date_str>/', views.detail, name='detail'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('stu_calendar/', views.stu_calendar_view, name='stu_calendar'),
    path('attendance_form/', views.attendance_form, name='attendance_form'),
    path('submit_attendance/', views.submit_attendance, name='submit_attendance'),
    path("attendance/summary/", views.attendance_summary, name="attendance_summary"),
    path('attendance/<str:date_str>/', views.attendance_detail, name='attendance_detail'),
    path('profile/<int:student_id>/', views.profile_view, name='profile'),
    path('student/account/', views.student_account_view, name='student_account'),
    path('student/reset_password/', views.student_reset_password_view, name='student_reset_password'),
    path('student/<int:student_id>/delete/', views.student_delete_view, name='student_delete_view'),
    path('student/<int:student_id>/hard-delete/',views.student_hard_delete_view,name='student_hard_delete'),
    path('student/delete-complete/<str:action>/', views.delete_complete_view, name='delete_complete'),
]
