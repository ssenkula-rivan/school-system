from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class AcademicYear(models.Model):
    """Academic Year/Session"""
    name = models.CharField(max_length=50, unique=True)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_current']),
            models.Index(fields=['-start_date']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other academic years to not current
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Grade(models.Model):
    """Grade/Class Level"""
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Form 1", "Primary 1"
    level = models.IntegerField()  # Numeric level for ordering
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['level']
        indexes = [
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return self.name


class Student(models.Model):
    """Student Information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
        ('suspended', 'Suspended'),
        ('expelled', 'Expelled'),
    ]
    
    SCHOLARSHIP_STATUS_CHOICES = [
        ('none', 'No Scholarship'),
        ('partial', 'Partial Scholarship'),
        ('full', 'Full Scholarship'),
    ]
    
    # Basic Information
    admission_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Academic Information
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, related_name='students')
    admission_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Scholarship Information
    scholarship_status = models.CharField(max_length=20, choices=SCHOLARSHIP_STATUS_CHOICES, default='none')
    scholarship_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))], help_text='Scholarship percentage (0-100)')
    scholarship_remarks = models.TextField(blank=True, help_text='Scholarship details and conditions')
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    
    # Guardian Information
    guardian_name = models.CharField(max_length=200)
    guardian_relationship = models.CharField(max_length=50)
    guardian_phone = models.CharField(max_length=15)
    guardian_email = models.EmailField(blank=True)
    guardian_address = models.TextField(blank=True)
    
    # Medical Information
    blood_group = models.CharField(max_length=5, blank=True, help_text='e.g., A+, O-, AB+')
    allergies = models.TextField(blank=True, help_text='List any known allergies')
    medical_conditions = models.TextField(blank=True, help_text='Any chronic conditions or special needs')
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    # Document Uploads
    birth_certificate = models.FileField(upload_to='student_documents/birth_certificates/', blank=True, null=True)
    previous_report_card = models.FileField(upload_to='student_documents/report_cards/', blank=True, null=True)
    transfer_certificate = models.FileField(upload_to='student_documents/transfers/', blank=True, null=True)
    other_documents = models.FileField(upload_to='student_documents/others/', blank=True, null=True)
    
    # System fields
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['admission_number']
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['status']),
            models.Index(fields=['grade', 'status']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['scholarship_status']),
            models.Index(fields=['status', 'scholarship_status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.admission_number} - {self.get_full_name()}"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def has_scholarship(self):
        """Check if student has any scholarship"""
        return self.scholarship_status != 'none' and self.scholarship_percentage > 0
    
    def calculate_fee_with_scholarship(self, original_fee):
        """Calculate fee after applying scholarship discount"""
        if not self.has_scholarship:
            return original_fee
        
        discount = original_fee * (self.scholarship_percentage / 100)
        return original_fee - discount
    
    def get_scholarship_amount(self, original_fee):
        """Get the scholarship discount amount"""
        if not self.has_scholarship:
            return Decimal('0.00')
        
        return original_fee * (self.scholarship_percentage / 100)


class FeeStructure(models.Model):
    """Fee Structure for different grades"""
    TERM_CHOICES = [
        ('1', 'Term 1'),
        ('2', 'Term 2'),
        ('3', 'Term 3'),
        ('annual', 'Annual'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_structures')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='fee_structures')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    
    # Fee Components
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    sports_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    uniform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['academic_year', 'grade', 'term']
        ordering = ['academic_year', 'grade', 'term']
        indexes = [
            models.Index(fields=['academic_year', 'grade']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.academic_year} - {self.grade} - {self.get_term_display()}"
    
    @property
    def total_fee(self):
        return (self.tuition_fee + self.registration_fee + self.library_fee + 
                self.sports_fee + self.lab_fee + self.transport_fee + 
                self.uniform_fee + self.exam_fee + self.other_fee)


class FeePayment(models.Model):
    """Fee Payment Records"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card Payment'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    receipt_number = models.CharField(max_length=50, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    
    # Additional Information
    transaction_reference = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'fee_structure']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['-payment_date']),
            models.Index(fields=['receipt_number']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.receipt_number} - {self.student.get_full_name()} - ${self.amount_paid}"


class FeeBalance(models.Model):
    """Track fee balances for students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_balances')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='balances')
    
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    scholarship_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Scholarship discount amount')
    amount_after_scholarship = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Amount after scholarship discount')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'fee_structure']
        ordering = ['student', 'fee_structure']
        indexes = [
            models.Index(fields=['student', 'is_paid']),
            models.Index(fields=['is_paid', 'due_date']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - Balance: ${self.balance}"
    
    def update_balance(self):
        """Recalculate balance based on payments and scholarship"""
        # Calculate scholarship discount
        self.scholarship_discount = self.student.get_scholarship_amount(self.total_fee)
        self.amount_after_scholarship = self.total_fee - self.scholarship_discount
        
        # Calculate total payments
        total_payments = self.student.payments.filter(
            fee_structure=self.fee_structure,
            payment_status='completed'
        ).aggregate(total=models.Sum('amount_paid'))['total'] or 0
        
        self.amount_paid = total_payments
        self.balance = self.amount_after_scholarship - self.amount_paid
        self.is_paid = self.balance <= 0
        self.save()
