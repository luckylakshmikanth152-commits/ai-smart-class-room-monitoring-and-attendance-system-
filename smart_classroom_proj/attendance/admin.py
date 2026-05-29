from django.contrib import admin
from .models import (Department, Faculty, Student, Subject, TimeTable,
                     Attendance, FacultyAttendance, BehaviourLog, Notification)

admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(TimeTable)
admin.site.register(Attendance)
admin.site.register(FacultyAttendance)
admin.site.register(BehaviourLog)
admin.site.register(Notification)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'department', 'email')
    search_fields = ('name', 'employee_id')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'department', 'section', 'semester')
    search_fields = ('name', 'roll_number')
    list_filter = ('department', 'section', 'semester')
