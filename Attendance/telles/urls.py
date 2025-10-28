from django.urls import path
from . import views

app_name = 'telles'

urlpatterns = [
    path('', views.index, name='index'),                # トップ画面
    path('attendance/', views.attendance, name='attendance'),  # 出欠簿
    path('logout/', views.logout_view, name='logout'),  # ログアウト
]
