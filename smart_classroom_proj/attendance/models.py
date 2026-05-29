from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='faculty_faces/')
    face_encoding = models.BinaryField(null=True, blank=True)  # stored as pickle

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=15)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    section = models.CharField(max_length=10, default='A')
    semester = models.IntegerField(default=1)
    photo = models.ImageField(upload_to='student_faces/')
    face_encoding = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class TimeTable(models.Model):
    DAYS = [
        ('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'),
        ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'),
    ]
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    section = models.CharField(max_length=10, default='A')
    semester = models.IntegerField(default=1)
    room = models.CharField(max_length=20, default='Room-101')

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.day} {self.start_time} - {self.subject.name} ({self.faculty.name})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Present')

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.date}"


class FacultyAttendance(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    arrival_time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=15, default='Present')  # Present / Late / Absent

    def __str__(self):
        return f"{self.faculty.name} - {self.date} - {self.status}"


class BehaviourLog(models.Model):
    BEHAVIOURS = [
        ('PHONE', 'Phone Usage'),
        ('SLEEP', 'Sleeping'),
        ('TALK', 'Talking'),
        ('ATTENTIVE', 'Attentive'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    behaviour = models.CharField(max_length=20, choices=BEHAVIOURS)
    confidence = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    snapshot = models.ImageField(upload_to='behaviour_snapshots/', null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student} - {self.behaviour} - {self.timestamp}"


class Notification(models.Model):
    TYPES = [
        ('FACULTY_ALERT', 'Faculty Class Alert'),
        ('FACULTY_ABSENT', 'Faculty Absent'),
        ('STUDENT_ABSENT', 'Student Absent'),
        ('BEHAVIOUR', 'Behaviour Alert'),
    ]
    notification_type = models.CharField(max_length=20, choices=TYPES)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient_email}"
