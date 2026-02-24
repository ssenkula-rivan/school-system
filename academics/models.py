from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from fees.models import Student, Grade, AcademicYear

class Subject(models.Model):
    """Academic subjects"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassSubject(models.Model):
    """Subject allocation to classes with teachers"""
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_allocations')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teaching_subjects')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='class_subjects')
    
    class Meta:
        unique_together = ['grade', 'subject', 'academic_year']
        ordering = ['grade', 'subject']
    
    def __str__(self):
        return f"{self.grade} - {self.subject} ({self.teacher.get_full_name() if self.teacher else 'No Teacher'})"


class Exam(models.Model):
    """Examination/Assessment"""
    EXAM_TYPE_CHOICES = [
        ('cat', 'Continuous Assessment Test'),
        ('midterm', 'Mid-Term Exam'),
        ('final', 'Final Exam'),
        ('mock', 'Mock Exam'),
    ]
    
    TERM_CHOICES = [
        ('1', 'Term 1'),
        ('2', 'Term 2'),
        ('3', 'Term 3'),
    ]
    
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='exams')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    max_marks = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    pass_marks = models.IntegerField(default=40, validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year} - Term {self.term}"


class Mark(models.Model):
    """Student marks/grades"""
    GRADE_CHOICES = [
        ('A', 'A - Excellent'),
        ('B', 'B - Very Good'),
        ('C', 'C - Good'),
        ('D', 'D - Satisfactory'),
        ('E', 'E - Pass'),
        ('F', 'F - Fail'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True)
    remarks = models.TextField(blank=True)
    
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='entered_marks')
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'exam']
        ordering = ['student', 'subject']
        indexes = [
            models.Index(fields=['student', 'exam']),
            models.Index(fields=['exam', 'subject']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.code} - {self.marks_obtained}/{self.exam.max_marks}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate grade
        percentage = (self.marks_obtained / self.exam.max_marks) * 100
        if percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B'
        elif percentage >= 60:
            self.grade = 'C'
        elif percentage >= 50:
            self.grade = 'D'
        elif percentage >= 40:
            self.grade = 'E'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)


class ReportCard(models.Model):
    """Student report cards"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='report_cards')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='report_cards')
    term = models.CharField(max_length=10, choices=Exam.TERM_CHOICES)
    
    total_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_grade = models.CharField(max_length=1, choices=Mark.GRADE_CHOICES, blank=True)
    class_rank = models.IntegerField(null=True, blank=True)
    
    teacher_comment = models.TextField(blank=True)
    headteacher_comment = models.TextField(blank=True)
    
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.academic_year} - Term {self.term}"
