from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    # Dashboard
    path('', views.fees_dashboard, name='dashboard'),
    path('bursar/', views.bursar_dashboard, name='bursar_dashboard'),
    
    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    
    # Fee Structure
    path('structure/', views.fee_structure_list, name='fee_structure_list'),
    path('structure/add/', views.fee_structure_create, name='fee_structure_create'),
    path('structure/<int:pk>/edit/', views.fee_structure_edit, name='fee_structure_edit'),
    
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    
    # Balances
    path('balances/', views.balance_list, name='balance_list'),
    path('balances/student/<int:student_id>/', views.student_balance, name='student_balance'),
    
    # Reports
    path('reports/', views.fee_reports, name='reports'),
    path('reports/defaulters/', views.defaulters_report, name='defaulters_report'),
]
