"""
complaints/views.py
────────────────────
Views:
  Citizen:
    dashboard        — stats + own complaints
    submit_complaint — new complaint form
    complaint_detail — view one complaint + QR
    track_complaint  — public tracking page (no login required)

  Admin:
    admin_dashboard  — global stats + all complaints
    admin_complaint_list — filterable list
    admin_complaint_detail — update status / assign dept
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import Complaint, Category, Department, StatusLog
from .forms import ComplaintForm, StatusUpdateForm, ComplaintFilterForm


# ─── Decorators ──────────────────────────────────────────────────────────────

def admin_required(view_func):
    """Redirect non-admins to citizen dashboard."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not request.user.is_civic_admin:
            messages.error(request, 'Admin access required.')
            return redirect('complaints:dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── Citizen views ────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    complaints = Complaint.objects.filter(user=request.user)
    stats = {
        'total':       complaints.count(),
        'submitted':   complaints.filter(status='submitted').count(),
        'in_progress': complaints.filter(status='in_progress').count(),
        'resolved':    complaints.filter(status='resolved').count(),
    }
    recent = complaints[:5]
    return render(request, 'complaints/dashboard.html', {
        'stats': stats,
        'recent_complaints': recent,
        'all_complaints': complaints,
    })


@login_required
def submit_complaint(request):
    form = ComplaintForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        complaint = form.save(commit=False)
        complaint.user = request.user
        complaint.save()
        messages.success(request,
            f'✅ Complaint submitted! Your ID is <strong>{complaint.complaint_id}</strong>.',
            extra_tags='safe')
        return redirect('complaints:complaint_detail', pk=complaint.pk)

    categories = Category.objects.all()
    return render(request, 'complaints/complaint_form.html', {
        'form': form,
        'categories': categories,
    })


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    # Citizens can only see own complaints
    if not request.user.is_civic_admin and complaint.user != request.user:
        return HttpResponseForbidden()
    logs = complaint.status_logs.select_related('changed_by')
    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'logs': logs,
    })


def track_complaint(request, complaint_id):
    """Public tracking — anyone with the ID can check status."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    logs = complaint.status_logs.select_related('changed_by')
    return render(request, 'complaints/track_complaint.html', {
        'complaint': complaint,
        'logs': logs,
    })


# ─── Admin views ──────────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    qs = Complaint.objects.all()
    stats = {
        'total':       qs.count(),
        'submitted':   qs.filter(status='submitted').count(),
        'in_progress': qs.filter(status='in_progress').count(),
        'resolved':    qs.filter(status='resolved').count(),
        'rejected':    qs.filter(status='rejected').count(),
    }
    by_category = (
        Category.objects.annotate(count=Count('complaint'))
                        .values('name', 'color', 'count')
    )
    recent = qs[:8]
    return render(request, 'complaints/admin_dashboard.html', {
        'stats': stats,
        'by_category': list(by_category),
        'recent_complaints': recent,
    })


@admin_required
def admin_complaint_list(request):
    qs = Complaint.objects.select_related('user', 'category', 'department')
    filter_form = ComplaintFilterForm(request.GET or None)

    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('category'):
            qs = qs.filter(category=data['category'])
        if data.get('status'):
            qs = qs.filter(status=data['status'])
        if data.get('search'):
            q = data['search']
            qs = qs.filter(
                Q(complaint_id__icontains=q) |
                Q(title__icontains=q) |
                Q(location_text__icontains=q) |
                Q(user__username__icontains=q)
            )

    return render(request, 'complaints/admin_complaint_list.html', {
        'complaints': qs,
        'filter_form': filter_form,
    })


@admin_required
def admin_complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    form = StatusUpdateForm(request.POST or None, instance=complaint)
    logs = complaint.status_logs.select_related('changed_by')

    if request.method == 'POST' and form.is_valid():
        old_status = complaint.status
        updated    = form.save(commit=False)
        new_status = updated.status

        # Record status change log
        if old_status != new_status:
            StatusLog.objects.create(
                complaint  = complaint,
                changed_by = request.user,
                old_status = old_status,
                new_status = new_status,
                note       = form.cleaned_data.get('admin_notes', ''),
            )
            # Send email notification to citizen
            _send_status_email(complaint, new_status)

        updated.save()
        messages.success(request, 'Complaint updated successfully.')
        return redirect('complaints:admin_complaint_detail', pk=pk)

    return render(request, 'complaints/admin_complaint_detail.html', {
        'complaint': complaint,
        'form': form,
        'logs': logs,
    })


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _send_status_email(complaint, new_status):
    """Send status-change notification email to the complaint owner."""
    subject = f'[SmartCivic] Complaint {complaint.complaint_id} — Status Update'
    message = (
        f'Dear {complaint.user.first_name or complaint.user.username},\n\n'
        f'Your complaint "{complaint.title}" (ID: {complaint.complaint_id}) '
        f'has been updated to: {complaint.get_status_display().upper()}.\n\n'
        f'Track your complaint at: '
        f'http://localhost:8000/complaints/track/{complaint.complaint_id}/\n\n'
        f'— SmartCivic Team'
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@smartcivic.local',
            [complaint.user.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Email errors should never crash the app
