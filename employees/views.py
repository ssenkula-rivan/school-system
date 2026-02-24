from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date, timedelta
from .models import Employee, Department, Position, LeaveRequest, PerformanceReview, Attendance
from .forms import EmployeeForm, LeaveRequestForm, PerformanceReviewForm # type: ignore
from accounts.decorators import can_manage_employees

@login_required
def employee_list(request):
    """Display list of all employees with filtering and search"""
    employees = Employee.objects.select_related('user', 'department', 'position').filter(
        employment_status='active'
    )
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )
    
    # Filter by department
    department_filter = request.GET.get('department')
    if department_filter:
        employees = employees.filter(department_id=department_filter)
    
    # Filter by employment type
    type_filter = request.GET.get('employment_type')
    if type_filter:
        employees = employees.filter(employment_type=type_filter)
    
    # Pagination
    paginator = Paginator(employees, 12)  # 12 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    departments = Department.objects.all()
    employment_types = Employee.EMPLOYMENT_TYPE
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'employment_types': employment_types,
        'search_query': search_query,
        'department_filter': department_filter,
        'type_filter': type_filter,
        'total_employees': employees.count(),
    }
    
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_detail(request, pk):
    """Display detailed employee information"""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Get recent performance reviews
    recent_reviews = employee.performance_reviews.order_by('-created_at')[:3]
    
    # Get recent leave requests
    recent_leaves = employee.leave_requests.order_by('-applied_on')[:5]
    
    # Get attendance summary for current month
    current_month = date.today().replace(day=1)
    attendance_records = employee.attendance_records.filter(
        date__gte=current_month
    )
    
    attendance_stats = {
        'present_days': attendance_records.filter(is_present=True).count(),
        'absent_days': attendance_records.filter(is_present=False).count(),
        'late_days': attendance_records.filter(is_late=True).count(),
        'avg_hours': attendance_records.aggregate(
            avg_hours=Avg('check_out__hour')
        )['avg_hours'] or 0
    }
    
    context = {
        'employee': employee,
        'recent_reviews': recent_reviews,
        'recent_leaves': recent_leaves,
        'attendance_stats': attendance_stats,
    }
    
    return render(request, 'employees/employee_detail.html', context)

@login_required
@can_manage_employees
def employee_create(request):
    """Create new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.user.get_full_name()} created successfully!')
            return redirect('employees:detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Add New Employee'
    })

@login_required
@can_manage_employees
def employee_edit(request, pk):
    """Edit employee information"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.user.get_full_name()} updated successfully!')
            return redirect('employees:detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'employee': employee,
        'title': f'Edit {employee.user.get_full_name()}'
    })

@login_required
def employee_dashboard(request):
    """Employee management dashboard with statistics"""
    # Get statistics
    total_employees = Employee.objects.filter(employment_status='active').count()
    total_departments = Department.objects.count()
    
    # Recent hires (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_hires = Employee.objects.filter(hire_date__gte=thirty_days_ago).count()
    
    # Pending leave requests
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    
    # Department wise employee count
    dept_stats = Department.objects.annotate(
        employee_count=Count('employees')
    ).order_by('-employee_count')[:5]
    
    # Recent activities
    recent_employees = Employee.objects.select_related('user', 'department').order_by('-created_at')[:5]
    recent_leaves = LeaveRequest.objects.select_related('employee__user').order_by('-applied_on')[:5]
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'recent_hires': recent_hires,
        'pending_leaves': pending_leaves,
        'dept_stats': dept_stats,
        'recent_employees': recent_employees,
        'recent_leaves': recent_leaves,
    }
    
    return render(request, 'employees/dashboard.html', context)

@login_required
def leave_requests(request):
    """Manage leave requests"""
    leaves = LeaveRequest.objects.select_related('employee__user', 'leave_type').order_by('-applied_on')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(leaves, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': LeaveRequest.STATUS_CHOICES,
    }
    
    return render(request, 'employees/leave_requests.html', context)

@login_required
def approve_leave(request, pk):
    """Approve or reject leave request"""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approved', 'rejected']:
            leave_request.status = action
            leave_request.approved_by = request.user
            leave_request.approved_on = timezone.now()
            leave_request.save()
            
            messages.success(request, f'Leave request {action} successfully!')
        
        return redirect('employees:leave_requests')
    
    return render(request, 'employees/leave_approve.html', {
        'leave_request': leave_request
    })

@login_required
def attendance_view(request):
    """View attendance records"""
    # Get current month attendance
    current_month = date.today().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    attendance_records = Attendance.objects.filter(
        date__gte=current_month,
        date__lt=next_month
    ).select_related('employee__user').order_by('-date')
    
    # Get summary statistics
    total_present = attendance_records.filter(is_present=True).count()
    total_absent = attendance_records.filter(is_present=False).count()
    total_late = attendance_records.filter(is_late=True).count()
    
    context = {
        'attendance_records': attendance_records,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_late': total_late,
        'current_month': current_month,
    }
    
    return render(request, 'employees/attendance.html', context)

@login_required
def performance_reviews(request):
    """View performance reviews"""
    reviews = PerformanceReview.objects.select_related('employee__user', 'reviewer').order_by('-created_at')
    
    # Filter by employee
    employee_filter = request.GET.get('employee')
    if employee_filter:
        reviews = reviews.filter(employee_id=employee_filter)
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    employees = Employee.objects.filter(employment_status='active')
    
    context = {
        'page_obj': page_obj,
        'employees': employees,
        'employee_filter': employee_filter,
    }
    
    return render(request, 'employees/performance_reviews.html', context)

# API Views for AJAX requests
@login_required
def employee_search_api(request):
    """API endpoint for employee search"""
    query = request.GET.get('q', '')
    employees = Employee.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(employee_id__icontains=query)
    ).select_related('user', 'department')[:10]
    
    results = []
    for employee in employees:
        results.append({
            'id': employee.id,
            'name': employee.user.get_full_name(),
            'employee_id': employee.employee_id,
            'department': employee.department.name if employee.department else '',
            'position': employee.position.title if employee.position else '',
        })
    
    return JsonResponse({'results': results})




# Role-specific dashboard views
@login_required
def teacher_dashboard(request):
    """Teacher-specific dashboard"""
    try:
        profile = request.user.userprofile
        if profile.role != 'teacher':
            messages.error(request, 'Access denied. Teachers only.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    from .models import WorkSubmission
    from accounts.models import UserProfile
    
    # Get teacher's submissions
    submissions = WorkSubmission.objects.filter(teacher=request.user).order_by('-submitted_at')[:10]
    
    # Statistics
    total_submissions = WorkSubmission.objects.filter(teacher=request.user).count()
    pending_submissions = WorkSubmission.objects.filter(teacher=request.user, status='pending').count()
    approved_submissions = WorkSubmission.objects.filter(teacher=request.user, status='approved').count()
    
    # Find who this teacher submits to
    submitted_to_name = "Director of Studies"
    if profile.class_name:
        head_of_class = UserProfile.objects.filter(
            role='head_of_class',
            class_name=profile.class_name,
            is_active_employee=True
        ).first()
        if head_of_class:
            submitted_to_name = f"Head of Class ({head_of_class.user.get_full_name()})"
    
    context = {
        'submissions': submissions,
        'total_submissions': total_submissions,
        'pending_submissions': pending_submissions,
        'approved_submissions': approved_submissions,
        'class_name': profile.class_name,
        'submitted_to_name': submitted_to_name,
    }
    
    return render(request, 'employees/teacher_dashboard.html', context)

@login_required
def director_dashboard(request):
    """Director-specific dashboard"""
    try:
        profile = request.user.userprofile
        if profile.role != 'director':
            messages.error(request, 'Access denied. Directors only.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    from .models import WorkSubmission
    from accounts.models import UserProfile
    
    # Get pending submissions from Heads of Class only
    pending_submissions = WorkSubmission.objects.filter(
        submitted_to=request.user,
        status='pending'
    ).select_related('teacher__userprofile').order_by('-submitted_at')[:10]
    
    # Statistics
    total_teachers = UserProfile.objects.filter(role='teacher', is_active_employee=True).count()
    total_heads = UserProfile.objects.filter(role='head_of_class', is_active_employee=True).count()
    total_submissions = WorkSubmission.objects.filter(submitted_to=request.user).count()
    pending_count = WorkSubmission.objects.filter(submitted_to=request.user, status='pending').count()
    approved_count = WorkSubmission.objects.filter(submitted_to=request.user, status='approved').count()
    
    context = {
        'pending_submissions': pending_submissions,
        'total_teachers': total_teachers,
        'total_heads': total_heads,
        'total_submissions': total_submissions,
        'pending_count': pending_count,
        'approved_count': approved_count,
    }
    
    return render(request, 'employees/director_dashboard.html', context)

@login_required
def head_of_class_dashboard(request):
    """Head of Class dashboard - reviews submissions from class teachers"""
    try:
        profile = request.user.userprofile
        if profile.role != 'head_of_class':
            messages.error(request, 'Access denied. Heads of Class only.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    from .models import WorkSubmission
    from accounts.models import UserProfile
    
    # Get pending submissions from teachers in this class
    pending_submissions = WorkSubmission.objects.filter(
        submitted_to=request.user,
        status='pending'
    ).select_related('teacher__userprofile').order_by('-submitted_at')[:10]
    
    # Get teachers in this class
    class_teachers = UserProfile.objects.filter(
        role='teacher',
        class_name=profile.class_name,
        is_active_employee=True
    ).select_related('user')
    
    # Statistics
    total_class_teachers = class_teachers.count()
    total_submissions = WorkSubmission.objects.filter(submitted_to=request.user).count()
    pending_count = WorkSubmission.objects.filter(submitted_to=request.user, status='pending').count()
    approved_count = WorkSubmission.objects.filter(submitted_to=request.user, status='approved').count()
    
    # My submissions to Director
    my_submissions = WorkSubmission.objects.filter(teacher=request.user).order_by('-submitted_at')[:5]
    my_pending = WorkSubmission.objects.filter(teacher=request.user, status='pending').count()
    
    context = {
        'pending_submissions': pending_submissions,
        'class_teachers': class_teachers,
        'total_class_teachers': total_class_teachers,
        'total_submissions': total_submissions,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'class_name': profile.class_name,
        'my_submissions': my_submissions,
        'my_pending': my_pending,
    }
    
    return render(request, 'employees/head_of_class_dashboard.html', context)

@login_required
def security_dashboard(request):
    """Security-specific dashboard"""
    try:
        profile = request.user.userprofile
        if profile.role != 'security':
            messages.error(request, 'Access denied. Security only.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    # Get today's attendance
    today = date.today()
    attendance_records = Attendance.objects.filter(date=today).select_related('employee__user')
    
    context = {
        'attendance_records': attendance_records,
        'today': today,
    }
    
    return render(request, 'employees/security_dashboard.html', context)

# Work submission views
@login_required
def submit_work(request):
    """Teacher submits work to Head of Class or DOS"""
    try:
        profile = request.user.userprofile
        if profile.role not in ['teacher', 'head_of_class']:
            messages.error(request, 'Only teachers and heads of class can submit work.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from .models import WorkSubmission
        from accounts.models import UserProfile
        
        title = request.POST.get('title')
        work_type = request.POST.get('work_type')
        description = request.POST.get('description')
        subject = request.POST.get('subject', '')
        grade_level = request.POST.get('grade_level', '')
        document = request.FILES.get('document')
        
        # Determine who to submit to based on role and class
        submitted_to_user = None
        
        if profile.role == 'teacher':
            # Regular teacher submits to Head of Class
            if profile.class_name:
                # Find Head of Class for this class
                head_of_class = UserProfile.objects.filter(
                    role='head_of_class',
                    class_name=profile.class_name,
                    is_active_employee=True
                ).first()
                
                if head_of_class:
                    submitted_to_user = head_of_class.user
                else:
                    # No Head of Class found, submit to Director
                    director = UserProfile.objects.filter(
                        role='director',
                        is_active_employee=True
                    ).first()
                    if director:
                        submitted_to_user = director.user
            else:
                # No class assigned, submit to Director
                director = UserProfile.objects.filter(
                    role='director',
                    is_active_employee=True
                ).first()
                if director:
                    submitted_to_user = director.user
        
        elif profile.role == 'head_of_class':
            # Head of Class submits to Director
            director = UserProfile.objects.filter(
                role='director',
                is_active_employee=True
            ).first()
            if director:
                submitted_to_user = director.user
        
        submission = WorkSubmission.objects.create(
            teacher=request.user,
            submitted_to=submitted_to_user,
            title=title,
            work_type=work_type,
            description=description,
            subject=subject,
            grade_level=grade_level,
            document=document
        )
        
        if profile.role == 'teacher':
            if submitted_to_user and hasattr(submitted_to_user, 'userprofile') and submitted_to_user.userprofile.role == 'head_of_class':
                messages.success(request, f'Work submitted successfully to Head of Class!')
            else:
                messages.success(request, f'Work submitted successfully to Director!')
        else:
            messages.success(request, 'Work submitted successfully to Director!')
        
        return redirect('employees:teacher_dashboard')
    
    from .models import WorkSubmission
    context = {
        'work_types': WorkSubmission.WORK_TYPE_CHOICES,
        'user_role': profile.role,
        'class_name': profile.class_name,
    }
    
    return render(request, 'employees/submit_work.html', context)

@login_required
def review_submissions(request):
    """Director or Head of Class reviews teacher submissions"""
    try:
        profile = request.user.userprofile
        if profile.role not in ['director', 'head_of_class']:
            messages.error(request, 'Only directors and heads of class can review submissions.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    from .models import WorkSubmission
    
    # Filter by status
    status_filter = request.GET.get('status', 'pending')
    
    # Only show submissions submitted to this user
    submissions = WorkSubmission.objects.filter(
        submitted_to=request.user,
        status=status_filter
    ).select_related('teacher__userprofile').order_by('-submitted_at')
    
    # Pagination
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'user_role': profile.role,
    }
    
    return render(request, 'employees/review_submissions.html', context)

@login_required
def review_submission_detail(request, pk):
    """Director or Head of Class reviews a specific submission"""
    try:
        profile = request.user.userprofile
        if profile.role not in ['director', 'head_of_class']:
            messages.error(request, 'Only directors and heads of class can review submissions.')
            return redirect('accounts:dashboard')
    except:
        messages.error(request, 'Profile not found.')
        return redirect('accounts:dashboard')
    
    from .models import WorkSubmission
    
    submission = get_object_or_404(WorkSubmission, pk=pk)
    
    # Ensure this submission was submitted to the current user
    if submission.submitted_to != request.user:
        messages.error(request, 'You can only review submissions submitted to you.')
        return redirect('employees:review_submissions')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '')
        
        if action in ['approved', 'rejected', 'revision']:
            submission.status = action
            submission.feedback = feedback
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.save()
            
            messages.success(request, f'Submission {action}!')
            return redirect('employees:review_submissions')
    
    context = {
        'submission': submission,
        'user_role': profile.role,
    }
    
    return render(request, 'employees/review_submission_detail.html', context)
