from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from datetime import date, timedelta
from .models import Student, FeeStructure, FeePayment, FeeBalance, AcademicYear, Grade
from accounts.decorators import can_manage_fees


@login_required
def bursar_dashboard(request):
    """Bursar-specific dashboard for fee management"""
    try:
        profile = request.user.userprofile
        if profile.role != 'bursar':
            messages.error(request, 'Access denied. Bursar only.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Financial Statistics
    total_students = Student.objects.filter(status='active').count()
    
    # Total expected revenue (all fee structures for current year)
    if current_year:
        total_expected = FeeBalance.objects.filter(
            fee_structure__academic_year=current_year
        ).aggregate(total=Sum('amount_after_scholarship'))['total'] or 0
    else:
        total_expected = 0
    
    # Total collected
    total_collected = FeePayment.objects.filter(
        payment_status='completed'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Total outstanding
    total_outstanding = FeeBalance.objects.filter(
        is_paid=False
    ).aggregate(total=Sum('balance'))['total'] or 0
    
    # Collection rate
    collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
    
    # Today's collections
    today_collections = FeePayment.objects.filter(
        payment_date=date.today(),
        payment_status='completed'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # This month's collections
    first_day_month = date.today().replace(day=1)
    month_collections = FeePayment.objects.filter(
        payment_date__gte=first_day_month,
        payment_status='completed'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Recent payments (last 10)
    recent_payments = FeePayment.objects.select_related(
        'student', 'fee_structure', 'received_by'
    ).order_by('-payment_date', '-created_at')[:10]
    
    # Defaulters (overdue balances)
    defaulters = FeeBalance.objects.filter(
        is_paid=False,
        due_date__lt=date.today()
    ).select_related('student', 'fee_structure').order_by('due_date')[:10]
    
    # Students with scholarships
    scholarship_students = Student.objects.filter(
        status='active',
        scholarship_status__in=['partial', 'full']
    ).count()
    
    # Payment methods breakdown (this month)
    payment_methods = FeePayment.objects.filter(
        payment_date__gte=first_day_month,
        payment_status='completed'
    ).values('payment_method').annotate(
        total=Sum('amount_paid'),
        count=Count('id')
    ).order_by('-total')
    
    # Pending payments count
    pending_count = FeeBalance.objects.filter(is_paid=False).count()
    
    context = {
        'current_year': current_year,
        'total_students': total_students,
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'collection_rate': round(collection_rate, 2),
        'today_collections': today_collections,
        'month_collections': month_collections,
        'recent_payments': recent_payments,
        'defaulters': defaulters,
        'scholarship_students': scholarship_students,
        'payment_methods': payment_methods,
        'pending_count': pending_count,
    }
    
    return render(request, 'fees/bursar_dashboard.html', context)


@login_required
def fees_dashboard(request):
    """Fees management dashboard"""
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Statistics
    total_students = Student.objects.filter(status='active').count()
    total_collected = FeePayment.objects.filter(payment_status='completed').aggregate(
        total=Sum('amount_paid'))['total'] or 0
    pending_payments = FeeBalance.objects.filter(is_paid=False).count()
    total_outstanding = FeeBalance.objects.filter(is_paid=False).aggregate(
        total=Sum('balance'))['total'] or 0
    
    # Recent payments
    recent_payments = FeePayment.objects.select_related('student', 'fee_structure').order_by('-payment_date')[:5]
    
    # Defaulters (students with overdue balances)
    defaulters = FeeBalance.objects.filter(
        is_paid=False,
        due_date__lt=date.today()
    ).select_related('student', 'fee_structure')[:10]
    
    context = {
        'current_year': current_year,
        'total_students': total_students,
        'total_collected': total_collected,
        'pending_payments': pending_payments,
        'total_outstanding': total_outstanding,
        'recent_payments': recent_payments,
        'defaulters': defaulters,
    }
    
    return render(request, 'fees/dashboard.html', context)


@login_required
def student_list(request):
    """List all students"""
    students = Student.objects.select_related('grade').filter(status='active')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(admission_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(guardian_name__icontains=search_query)
        )
    
    # Filter by grade
    grade_filter = request.GET.get('grade')
    if grade_filter:
        students = students.filter(grade_id=grade_filter)
    
    # Filter by scholarship status
    scholarship_filter = request.GET.get('scholarship')
    if scholarship_filter:
        students = students.filter(scholarship_status=scholarship_filter)
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    grades = Grade.objects.all()
    
    # Statistics
    total_students = Student.objects.filter(status='active').count()
    scholarship_students = Student.objects.filter(status='active', scholarship_status__in=['partial', 'full']).count()
    full_scholarship = Student.objects.filter(status='active', scholarship_status='full').count()
    partial_scholarship = Student.objects.filter(status='active', scholarship_status='partial').count()
    
    context = {
        'page_obj': page_obj,
        'grades': grades,
        'search_query': search_query,
        'grade_filter': grade_filter,
        'scholarship_filter': scholarship_filter,
        'total_students': total_students,
        'scholarship_students': scholarship_students,
        'full_scholarship': full_scholarship,
        'partial_scholarship': partial_scholarship,
        'scholarship_choices': Student.SCHOLARSHIP_STATUS_CHOICES,
    }
    
    return render(request, 'fees/student_list.html', context)


@login_required
def student_detail(request, pk):
    """Student detail with fee information"""
    student = get_object_or_404(Student, pk=pk)
    
    # Get fee balances
    balances = student.fee_balances.select_related('fee_structure').all()
    
    # Get payment history
    payments = student.payments.select_related('fee_structure').order_by('-payment_date')
    
    # Calculate totals
    total_fees = balances.aggregate(total=Sum('total_fee'))['total'] or 0
    total_scholarship = balances.aggregate(total=Sum('scholarship_discount'))['total'] or 0
    total_after_scholarship = balances.aggregate(total=Sum('amount_after_scholarship'))['total'] or 0
    total_paid = balances.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_balance = balances.aggregate(total=Sum('balance'))['total'] or 0
    
    context = {
        'student': student,
        'balances': balances,
        'payments': payments,
        'total_fees': total_fees,
        'total_scholarship': total_scholarship,
        'total_after_scholarship': total_after_scholarship,
        'total_paid': total_paid,
        'total_balance': total_balance,
    }
    
    return render(request, 'fees/student_detail.html', context)


@login_required
def student_create(request):
    """Create new student"""
    # This would use a form - simplified for now
    return render(request, 'fees/student_form.html', {'title': 'Add New Student'})


@login_required
def student_edit(request, pk):
    """Edit student information"""
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'fees/student_form.html', {'student': student, 'title': 'Edit Student'})


@login_required
def fee_structure_list(request):
    """List fee structures"""
    structures = FeeStructure.objects.select_related('academic_year', 'grade').filter(is_active=True)
    
    # Filter by academic year
    year_filter = request.GET.get('year')
    if year_filter:
        structures = structures.filter(academic_year_id=year_filter)
    
    academic_years = AcademicYear.objects.all()
    
    context = {
        'structures': structures,
        'academic_years': academic_years,
        'year_filter': year_filter,
    }
    
    return render(request, 'fees/fee_structure_list.html', context)


@login_required
def fee_structure_create(request):
    """Create fee structure"""
    return render(request, 'fees/fee_structure_form.html', {'title': 'Create Fee Structure'})


@login_required
def fee_structure_edit(request, pk):
    """Edit fee structure"""
    structure = get_object_or_404(FeeStructure, pk=pk)
    return render(request, 'fees/fee_structure_form.html', {'structure': structure, 'title': 'Edit Fee Structure'})


@login_required
def payment_list(request):
    """List all payments"""
    payments = FeePayment.objects.select_related('student', 'fee_structure', 'received_by').order_by('-payment_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    
    return render(request, 'fees/payment_list.html', context)


@login_required
def payment_create(request):
    """Create new payment"""
    return render(request, 'fees/payment_form.html', {'title': 'Record Payment'})


@login_required
def payment_detail(request, pk):
    """Payment detail"""
    payment = get_object_or_404(FeePayment, pk=pk)
    return render(request, 'fees/payment_detail.html', {'payment': payment})


@login_required
def payment_receipt(request, pk):
    """Generate payment receipt"""
    payment = get_object_or_404(FeePayment, pk=pk)
    return render(request, 'fees/payment_receipt.html', {'payment': payment})


@login_required
def balance_list(request):
    """List fee balances"""
    balances = FeeBalance.objects.select_related('student', 'fee_structure').filter(is_paid=False)
    
    # Pagination
    paginator = Paginator(balances, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'fees/balance_list.html', context)


@login_required
def student_balance(request, student_id):
    """Student specific balance"""
    student = get_object_or_404(Student, pk=student_id)
    balances = student.fee_balances.select_related('fee_structure').all()
    
    context = {
        'student': student,
        'balances': balances,
    }
    
    return render(request, 'fees/student_balance.html', context)


@login_required
def fee_reports(request):
    """Fee reports dashboard"""
    return render(request, 'fees/reports.html')


@login_required
def defaulters_report(request):
    """Report of students with outstanding fees"""
    defaulters = FeeBalance.objects.filter(
        is_paid=False,
        due_date__lt=date.today()
    ).select_related('student', 'fee_structure').order_by('due_date')
    
    context = {
        'defaulters': defaulters,
    }
    
    return render(request, 'fees/defaulters_report.html', context)
