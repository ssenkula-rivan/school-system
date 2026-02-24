from django.contrib import admin
from .models import AcademicYear, Grade, Student, FeeStructure, FeePayment, FeeBalance


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    search_fields = ['name']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'description']
    ordering = ['level']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'get_full_name', 'grade', 'status', 'admission_date']
    list_filter = ['status', 'grade', 'gender']
    search_fields = ['admission_number', 'first_name', 'last_name', 'guardian_name']
    date_hierarchy = 'admission_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('admission_number', 'first_name', 'middle_name', 'last_name', 
                      'date_of_birth', 'gender', 'photo')
        }),
        ('Academic Information', {
            'fields': ('grade', 'admission_date', 'status')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_relationship', 'guardian_phone', 
                      'guardian_email', 'guardian_address')
        }),
    )


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'grade', 'term', 'total_fee', 'is_active']
    list_filter = ['academic_year', 'grade', 'term', 'is_active']
    search_fields = ['grade__name', 'academic_year__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('academic_year', 'grade', 'term', 'is_active', 'description')
        }),
        ('Fee Components', {
            'fields': ('tuition_fee', 'registration_fee', 'library_fee', 'sports_fee',
                      'lab_fee', 'transport_fee', 'uniform_fee', 'exam_fee', 'other_fee')
        }),
    )


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'amount_paid', 'payment_date', 
                   'payment_method', 'payment_status', 'received_by']
    list_filter = ['payment_status', 'payment_method', 'payment_date']
    search_fields = ['receipt_number', 'student__admission_number', 'student__first_name', 
                    'student__last_name', 'transaction_reference']
    date_hierarchy = 'payment_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FeeBalance)
class FeeBalanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'total_fee', 'amount_paid', 'balance', 'is_paid']
    list_filter = ['is_paid', 'fee_structure__academic_year', 'fee_structure__grade']
    search_fields = ['student__admission_number', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'updated_at']
