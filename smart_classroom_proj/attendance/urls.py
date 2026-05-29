from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('live/', views.live_view, name='live'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),

    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    path('faculty/', views.faculty_list, name='faculty_list'),
    path('faculty/add/', views.faculty_add, name='faculty_add'),
    path('faculty/<int:pk>/delete/', views.faculty_delete, name='faculty_delete'),

    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/behaviour/', views.behaviour_report, name='behaviour_report'),
    path('timetable/', views.timetable_view, name='timetable'),
]
