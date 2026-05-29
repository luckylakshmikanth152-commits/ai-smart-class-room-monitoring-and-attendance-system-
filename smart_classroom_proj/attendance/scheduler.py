"""APScheduler — runs every minute, checks timetable, sends alerts."""
from datetime import datetime, timedelta
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore


def check_upcoming_classes():
    """Send 10-min advance reminders to faculty."""
    from .models import TimeTable, Notification
    from .notifications import send_faculty_class_alert

    now = timezone.localtime()
    target = now + timedelta(minutes=10)
    day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT'}
    today = day_map.get(now.weekday())
    if not today:
        return

    classes = TimeTable.objects.filter(
        day=today,
        start_time__hour=target.hour,
        start_time__minute=target.minute,
    )
    for c in classes:
        # Avoid duplicates - check if alert already sent today
        already = Notification.objects.filter(
            notification_type='FACULTY_ALERT',
            recipient_email=c.faculty.email,
            sent_at__date=now.date(),
            subject__icontains=c.subject.name,
        ).exists()
        if not already:
            send_faculty_class_alert(c.faculty, c)


def check_late_faculty():
    """Check 10 mins after class start; if faculty not arrived -> alert HOD/Principal."""
    from .models import TimeTable, FacultyAttendance
    from .notifications import send_faculty_absent_alert

    now = timezone.localtime()
    target = now - timedelta(minutes=10)
    day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT'}
    today = day_map.get(now.weekday())
    if not today:
        return

    classes = TimeTable.objects.filter(
        day=today,
        start_time__hour=target.hour,
        start_time__minute=target.minute,
    )
    for c in classes:
        attended = FacultyAttendance.objects.filter(
            faculty=c.faculty, timetable=c, date=now.date()
        ).exists()
        if not attended:
            # Configure these in admin / env
            HOD_EMAIL = 'hod@example.com'
            PRINCIPAL_EMAIL = 'principal@example.com'
            send_faculty_absent_alert(c.faculty, c, HOD_EMAIL, PRINCIPAL_EMAIL)


def notify_absent_students():
    """End-of-day: notify parents of absent students."""
    from .models import Student, Attendance, TimeTable
    from .notifications import send_student_absent_email

    now = timezone.localtime()
    day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT'}
    today = day_map.get(now.weekday())
    if not today:
        return

    todays_classes = TimeTable.objects.filter(day=today)
    for cls in todays_classes:
        students = Student.objects.filter(
            department=cls.department, section=cls.section, semester=cls.semester
        )
        for s in students:
            present = Attendance.objects.filter(
                student=s, subject=cls.subject, date=now.date()
            ).exists()
            if not present:
                send_student_absent_email(s, cls.subject.name, str(now.date()))


def start_scheduler():
    scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(check_upcoming_classes, 'interval', minutes=1,
                      id='upcoming_classes', replace_existing=True)
    scheduler.add_job(check_late_faculty, 'interval', minutes=1,
                      id='late_faculty', replace_existing=True)
    scheduler.add_job(notify_absent_students, 'cron', hour=18, minute=0,
                      id='absent_students', replace_existing=True)
    scheduler.start()
    print("[Scheduler] Started.")
