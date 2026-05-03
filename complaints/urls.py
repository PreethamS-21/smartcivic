"""
complaints/urls.py
"""

from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    # ── Citizen ───────────────────────────────────────────────────────────────
    path('dashboard/',           views.dashboard,          name='dashboard'),
    path('submit/',              views.submit_complaint,   name='submit_complaint'),
    path('<int:pk>/',            views.complaint_detail,   name='complaint_detail'),
    path('track/<str:complaint_id>/', views.track_complaint, name='track_complaint'),

    # ── Admin ──────────────────────────────────────────────────────────────────
    path('admin/',               views.admin_dashboard,        name='admin_dashboard'),
    path('admin/complaints/',    views.admin_complaint_list,   name='admin_complaint_list'),
    path('admin/complaints/<int:pk>/', views.admin_complaint_detail, name='admin_complaint_detail'),
]
