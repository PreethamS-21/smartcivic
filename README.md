# SmartCivic — Smart Civic Issue Reporting System
## Complete Setup Guide (Step-by-Step)

---

## 📁 Project Structure

```
SmartCivicSystem/
├── civic_project/          ← Django project config
│   ├── settings.py         ← All settings (DB, email, maps, etc.)
│   ├── urls.py             ← Root URL dispatcher
│   └── wsgi.py
├── users/                  ← User auth app
│   ├── models.py           ← CustomUser (role: citizen/admin)
│   ├── views.py            ← register, login, logout, profile
│   ├── forms.py            ← Registration + login forms
│   ├── urls.py
│   └── admin.py
├── complaints/             ← Core complaints app
│   ├── models.py           ← Category, Department, Complaint, StatusLog
│   ├── views.py            ← All citizen + admin views
│   ├── forms.py            ← Complaint + filter forms
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_data.py ← Sample data loader
├── templates/
│   ├── partials/base.html  ← Master layout + navbar
│   ├── users/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   └── complaints/
│       ├── dashboard.html           ← Citizen dashboard
│       ├── complaint_form.html      ← Submit complaint + Maps
│       ├── complaint_detail.html    ← View + QR code
│       ├── track_complaint.html     ← Public tracker (no login)
│       ├── admin_dashboard.html     ← Admin stats + charts
│       ├── admin_complaint_list.html← Filterable list
│       └── admin_complaint_detail.html ← Manage complaint
├── static/
│   └── css/main.css        ← Complete design system
├── manage.py
└── requirements.txt
```

---

## ⚙️ STEP 1 — Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

---

## ⚙️ STEP 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt includes:**
- Django 4.2
- Pillow (image uploads)
- qrcode[pil] (QR code generation)
- django-crispy-forms + crispy-bootstrap5

---

## ⚙️ STEP 3 — Configure Settings

Open `civic_project/settings.py` and update:

### Google Maps API Key
```python
GOOGLE_MAPS_API_KEY = 'YOUR_ACTUAL_KEY_HERE'
```
Get a free key at: https://console.cloud.google.com → Enable **Maps JavaScript API** + **Geocoding API**

### Email (for status notifications)
```python
# For development — prints emails to console:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production with Gmail:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'   # Gmail App Password
```

### MySQL (optional — SQLite works out of the box)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smart_civic_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
Then create the database:
```sql
CREATE DATABASE smart_civic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## ⚙️ STEP 4 — Run Migrations

```bash
python manage.py makemigrations users
python manage.py makemigrations complaints
python manage.py migrate
```

---

## ⚙️ STEP 5 — Load Sample Data

```bash
python manage.py seed_data
```

This creates:
| Account   | Username   | Password    | Role  |
|-----------|------------|-------------|-------|
| Admin     | admin      | admin123    | Admin |
| Citizen   | citizen1   | citizen123  | Citizen |

Plus 6 categories, 6 departments, and 5 sample complaints.

---

## ⚙️ STEP 6 — Run the Server

```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

---

## 🌐 URL Map

| URL | Description |
|-----|-------------|
| `/users/login/` | Login page |
| `/users/register/` | Citizen registration |
| `/users/logout/` | Logout |
| `/users/profile/` | Edit profile |
| `/complaints/dashboard/` | Citizen dashboard |
| `/complaints/submit/` | Submit new complaint |
| `/complaints/<id>/` | View complaint detail + QR |
| `/complaints/track/<CIV_ID>/` | Public complaint tracker (no login) |
| `/complaints/admin/` | Admin dashboard with charts |
| `/complaints/admin/complaints/` | All complaints with filters |
| `/complaints/admin/complaints/<id>/` | Manage complaint status |
| `/django-admin/` | Django built-in admin |

---

## 🗄️ Database Schema

### CustomUser
| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| username | CharField | unique |
| email | EmailField | |
| first_name | CharField | |
| last_name | CharField | |
| role | CharField | 'citizen' or 'admin' |
| phone | CharField | optional |
| avatar | ImageField | upload_to='avatars/' |

### Category
| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| name | CharField | unique |
| icon | CharField | bootstrap-icon name |
| color | CharField | hex color |
| description | TextField | |

### Department
| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| name | CharField | unique |
| email | EmailField | for notifications |

### Complaint
| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| complaint_id | CharField | e.g. CIV3A7F2B (auto) |
| user | FK → CustomUser | |
| category | FK → Category | |
| department | FK → Department | nullable |
| title | CharField | |
| description | TextField | |
| image | ImageField | upload_to='complaints/' |
| location_text | CharField | human address |
| latitude | DecimalField | from Google Maps |
| longitude | DecimalField | from Google Maps |
| status | CharField | submitted/in_progress/resolved/rejected |
| admin_notes | TextField | visible to citizen |
| qr_code | ImageField | auto-generated PNG |
| created_at | DateTimeField | auto |
| updated_at | DateTimeField | auto |

### StatusLog
| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| complaint | FK → Complaint | |
| changed_by | FK → CustomUser | |
| old_status | CharField | |
| new_status | CharField | |
| note | TextField | |
| changed_at | DateTimeField | auto |

---

## 🔐 Security Features

- CSRF protection on all forms (Django built-in)
- `@login_required` on all authenticated views
- `@admin_required` custom decorator for admin views
- Role-based access: citizens can only see their own complaints
- Password validation (length, common passwords, similarity)
- `HttpResponseForbidden` if citizen tries to view another's complaint

---

## 🚀 Production Deployment (Checklist)

```python
# settings.py changes for production:
DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']   # use env var
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

```bash
# Collect static files
python manage.py collectstatic

# Use gunicorn
pip install gunicorn
gunicorn civic_project.wsgi:application --bind 0.0.0.0:8000
```

Use **Nginx** as reverse proxy + **Let's Encrypt** for HTTPS.

---

## 📦 Features Summary

| Feature | Implementation |
|---------|---------------|
| User Registration/Login | CustomUser model + Django auth |
| Role-based Access | citizen / admin roles + decorators |
| Complaint Submission | ComplaintForm with image upload |
| Google Maps Location Picker | Maps JS API + Geocoding API |
| Unique Complaint ID | Auto CIV + 6 hex chars (e.g. CIV3A7F2B) |
| QR Code Generation | qrcode[pil] library, auto on save |
| Status Tracking | submitted → in_progress → resolved |
| Status History Log | StatusLog model with timestamps |
| Email Notifications | send_mail on status change |
| Admin Dashboard | Charts.js doughnut + bar chart |
| Filter Complaints | By category, status, search query |
| Department Assignment | FK to Department model |
| Public Tracker | No login needed, scan QR code |
| CSRF Protection | Django middleware |
| Responsive UI | Bootstrap 5 + custom dark theme |
