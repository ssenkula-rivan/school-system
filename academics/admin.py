from django.contrib import admin
from .models import Subject, ClassSubject, Exam, Mark, ReportCard

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    search_fields = ['name', 'code']

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['grade', 'subject', 'teacher', 'academic_year']
    list_filter = ['grade', 'academic_year']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'term', 'start_date']
    list_filter = ['exam_type', 'academic_year', 'term']

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam', 'marks_obtained', 'grade']
    list_filter = ['exam', 'subject']

@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'term', 'generated_at']
    list_filter = ['academic_year', 'term']
