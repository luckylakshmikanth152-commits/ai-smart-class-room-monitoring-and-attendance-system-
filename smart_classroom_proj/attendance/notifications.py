"""Email notifications."""
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification


def _send(notification_type, recipient, subject, message):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [recipient], fail_silently=False)
        sent = True
    except Exception as e:
        print(f"[Notification] Email failed: {e}")
        sent = False
    Notification.objects.create(
        notification_type=notification_type,
        recipient_email=recipient,
        subject=subject,
        message=message,
        is_sent=sent,
    )


def send_faculty_class_alert(faculty, timetable_entry):
    subject = f"Class Reminder: {timetable_entry.subject.name} in 10 minutes"
    message = (f"Dear {faculty.name},\n\n"
               f"You have a class scheduled:\n"
               f"  Subject: {timetable_entry.subject.name}\n"
               f"  Time: {timetable_entry.start_time}\n"
               f"  Room: {timetable_entry.room}\n\n"
               f"Please be on time.\n\nSmart Classroom System")
    _send('FACULTY_ALERT', faculty.email, subject, message)


def send_faculty_absent_alert(faculty, timetable_entry, hod_email, principal_email):
    subject = f"Faculty Absent/Late: {faculty.name}"
    message = (f"Faculty {faculty.name} has not arrived for the scheduled class:\n"
               f"  Subject: {timetable_entry.subject.name}\n"
               f"  Time: {timetable_entry.start_time}\n"
               f"  Room: {timetable_entry.room}\n\n"
               f"Please take action.\n\nSmart Classroom System")
    for r in [hod_email, principal_email]:
        if r:
            _send('FACULTY_ABSENT', r, subject, message)


def send_student_absent_email(student, subject_name, date_str):
    email_subject = f"Absence Notice: {student.name} on {date_str}"
    message = (f"Dear Parent,\n\n"
               f"Your ward {student.name} (Roll: {student.roll_number}) "
               f"was marked absent for {subject_name} on {date_str}.\n\n"
               f"Please contact the institute for details.\n\n"
               f"Avanthi Institute of Engineering and Technology")
    _send('STUDENT_ABSENT', student.parent_email, email_subject, message)
