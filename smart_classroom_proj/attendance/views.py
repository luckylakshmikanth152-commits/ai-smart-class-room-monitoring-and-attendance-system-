from django.shortcuts import render, redirect, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta, date

from .models import (Student, Faculty, Attendance, FacultyAttendance,
                     BehaviourLog, TimeTable, Subject, Department, Notification)
from .forms import StudentForm, FacultyForm
from .face_engine import encode_face_from_image, FaceEngine
from .camera import gen_frames, release_camera, get_current_class


def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'attendance/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    today = date.today()
    ctx = {
        'total_students': Student.objects.count(),
        'total_faculty': Faculty.objects.count(),
        'total_subjects': Subject.objects.count(),
        'today_attendance': Attendance.objects.filter(date=today).count(),
        'today_behaviour': BehaviourLog.objects.filter(timestamp__date=today).count(),
        'current_class': get_current_class(),
        'recent_attendance': Attendance.objects.select_related('student', 'subject')[:10],
        'recent_behaviour': BehaviourLog.objects.select_related('student', 'subject')[:10],
    }
    return render(request, 'attendance/dashboard.html', ctx)


@login_required
def live_view(request):
    behaviour = request.GET.get('behaviour', '0') == '1'
    return render(request, 'attendance/live.html', {'behaviour': behaviour})


@login_required
def video_feed(request):
    behaviour_on = request.GET.get('behaviour', '0') == '1'
    return StreamingHttpResponse(
        gen_frames(behaviour_on=behaviour_on),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


@login_required
def stop_camera(request):
    release_camera()
    return JsonResponse({'status': 'stopped'})


# --- Student CRUD ---
@login_required
def student_list(request):
    students = Student.objects.select_related('department').all()
    return render(request, 'attendance/student_list.html', {'students': students})


@login_required
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            # Encode face
            enc = encode_face_from_image(student.photo.path)
            if enc:
                student.face_encoding = enc
                student.save()
                FaceEngine().load_encodings()  # reload
                messages.success(request, f'{student.name} added with face encoding.')
            else:
                messages.warning(request, f'{student.name} added but no face detected in photo.')
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'attendance/form.html', {'form': form, 'title': 'Add Student'})


@login_required
def student_delete(request, pk):
    s = get_object_or_404(Student, pk=pk)
    s.delete()
    FaceEngine().load_encodings()
    messages.success(request, 'Student deleted.')
    return redirect('student_list')


# --- Faculty CRUD ---
@login_required
def faculty_list(request):
    faculty = Faculty.objects.select_related('department').all()
    return render(request, 'attendance/faculty_list.html', {'faculty': faculty})


@login_required
def faculty_add(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save()
            enc = encode_face_from_image(f.photo.path)
            if enc:
                f.face_encoding = enc
                f.save()
                FaceEngine().load_encodings()
                messages.success(request, f'{f.name} added with face encoding.')
            else:
                messages.warning(request, f'{f.name} added but no face detected in photo.')
            return redirect('faculty_list')
    else:
        form = FacultyForm()
    return render(request, 'attendance/form.html', {'form': form, 'title': 'Add Faculty'})


@login_required
def faculty_delete(request, pk):
    f = get_object_or_404(Faculty, pk=pk)
    f.delete()
    FaceEngine().load_encodings()
    return redirect('faculty_list')


# --- Reports ---
@login_required
def attendance_report(request):
    qs = Attendance.objects.select_related('student', 'subject', 'faculty')
    student_id = request.GET.get('student')
    subject_id = request.GET.get('subject')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    if student_id:
        qs = qs.filter(student_id=student_id)
    if subject_id:
        qs = qs.filter(subject_id=subject_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    return render(request, 'attendance/report.html', {
        'records': qs[:500],
        'students': Student.objects.all(),
        'subjects': Subject.objects.all(),
    })


@login_required
def behaviour_report(request):
    logs = BehaviourLog.objects.select_related('student', 'subject')[:200]
    summary = BehaviourLog.objects.values('behaviour').annotate(c=Count('id'))
    return render(request, 'attendance/behaviour_report.html', {
        'logs': logs, 'summary': summary,
    })


@login_required
def timetable_view(request):
    tt = TimeTable.objects.select_related('subject', 'faculty', 'department').all()
    return render(request, 'attendance/timetable.html', {'timetable': tt})
