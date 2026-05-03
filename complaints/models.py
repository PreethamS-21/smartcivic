"""
complaints/models.py
────────────────────
Core models:
  • Category   — Garbage, Pothole, Streetlight, etc.
  • Department — Sanitation, Roads, Electricity, etc.
  • Complaint  — Main complaint record with status flow
  • StatusLog  — History of every status change
"""

import uuid
import qrcode
import io
from PIL import Image
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile


# ─── Category ────────────────────────────────────────────────────────────────

class Category(models.Model):
    ICON_CHOICES = [
        ('trash',      '🗑️ Garbage'),
        ('road',       '🕳️ Pothole / Road'),
        ('lightbulb',  '💡 Streetlight'),
        ('droplet',    '💧 Water Leakage'),
        ('water',      '🌊 Drainage'),
        ('tools',      '🔧 Others'),
    ]

    name        = models.CharField(max_length=100, unique=True)
    icon        = models.CharField(max_length=20, choices=ICON_CHOICES, default='tools')
    description = models.TextField(blank=True)
    color       = models.CharField(max_length=7, default='#6366f1',
                                   help_text='Hex color for badges, e.g. #ff5733')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


# ─── Department ──────────────────────────────────────────────────────────────

class Department(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    email       = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ─── Complaint ────────────────────────────────────────────────────────────────

class Complaint(models.Model):
    STATUS_SUBMITTED   = 'submitted'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED    = 'resolved'
    STATUS_REJECTED    = 'rejected'

    STATUS_CHOICES = [
        (STATUS_SUBMITTED,   'Submitted'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESOLVED,    'Resolved'),
        (STATUS_REJECTED,    'Rejected'),
    ]

    STATUS_COLORS = {
        STATUS_SUBMITTED:   'warning',
        STATUS_IN_PROGRESS: 'info',
        STATUS_RESOLVED:    'success',
        STATUS_REJECTED:    'danger',
    }

    # ── Identity ──────────────────────────────────────────────────────────────
    complaint_id = models.CharField(max_length=12, unique=True, editable=False)

    # ── Relations ─────────────────────────────────────────────────────────────
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='complaints')
    category   = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='complaints')

    # ── Content ───────────────────────────────────────────────────────────────
    title       = models.CharField(max_length=200)
    description = models.TextField()
    image       = models.ImageField(upload_to='complaints/', blank=True, null=True)

    # ── Location ──────────────────────────────────────────────────────────────
    location_text = models.CharField(max_length=300, help_text='Human-readable address')
    latitude      = models.DecimalField(max_digits=9, decimal_places=6,
                                        null=True, blank=True)
    longitude     = models.DecimalField(max_digits=9, decimal_places=6,
                                        null=True, blank=True)

    # ── Status ────────────────────────────────────────────────────────────────
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                    default=STATUS_SUBMITTED)
    admin_notes  = models.TextField(blank=True, help_text='Internal notes from admin')

    # ── QR Code ───────────────────────────────────────────────────────────────
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.complaint_id}] {self.title}'

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def status_badge(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def generate_complaint_id(self):
        """CIV + 6 uppercase hex chars, e.g. CIV3A7F2B"""
        return 'CIV' + uuid.uuid4().hex[:6].upper()

    def generate_qr_code(self):
        """Creates a QR PNG pointing to the complaint tracking URL."""
        tracking_url = f"http://localhost:8000/complaints/track/{self.complaint_id}/"
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(tracking_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1e293b", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.complaint_id}.png'
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        # Assign unique ID on first save
        if not self.complaint_id:
            cid = self.generate_complaint_id()
            while Complaint.objects.filter(complaint_id=cid).exists():
                cid = self.generate_complaint_id()
            self.complaint_id = cid
        # Generate QR if missing
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)


# ─── StatusLog ───────────────────────────────────────────────────────────────

class StatusLog(models.Model):
    complaint  = models.ForeignKey(Complaint, on_delete=models.CASCADE,
                                   related_name='status_logs')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    note       = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.complaint.complaint_id}: {self.old_status} → {self.new_status}'
