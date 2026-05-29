from django import forms
from .models import Student, Faculty


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ('face_encoding',)


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        exclude = ('face_encoding', 'user')
