"""
complaints/management/commands/seed_data.py
────────────────────────────────────────────
Run:  python manage.py seed_data
Creates categories, departments, admin user, sample citizen + complaints.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from complaints.models import Category, Department, Complaint

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample data for demo/testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱  Seeding database...')

        # ── Categories ────────────────────────────────────────────────────
        categories = [
            {'name': 'Garbage',        'icon': 'trash',     'color': '#ef4444'},
            {'name': 'Pothole / Road', 'icon': 'road',      'color': '#f59e0b'},
            {'name': 'Streetlight',    'icon': 'lightbulb', 'color': '#eab308'},
            {'name': 'Water Leakage',  'icon': 'droplet',   'color': '#38bdf8'},
            {'name': 'Drainage',       'icon': 'water',     'color': '#6366f1'},
            {'name': 'Others',         'icon': 'tools',     'color': '#8b5cf6'},
        ]
        cat_objects = {}
        for c in categories:
            obj, _ = Category.objects.get_or_create(name=c['name'], defaults=c)
            cat_objects[c['name']] = obj
        self.stdout.write(f'  ✅  {len(categories)} categories ready')

        # ── Departments ───────────────────────────────────────────────────
        departments = [
            {'name': 'Sanitation & Waste',  'email': 'sanitation@civic.local'},
            {'name': 'Roads & Infrastructure', 'email': 'roads@civic.local'},
            {'name': 'Electricity Board',   'email': 'electricity@civic.local'},
            {'name': 'Water Supply Board',  'email': 'water@civic.local'},
            {'name': 'Storm Drain Division','email': 'drainage@civic.local'},
            {'name': 'General Works',       'email': 'general@civic.local'},
        ]
        dept_objects = {}
        for d in departments:
            obj, _ = Department.objects.get_or_create(name=d['name'], defaults=d)
            dept_objects[d['name']] = obj
        self.stdout.write(f'  ✅  {len(departments)} departments ready')

        # ── Admin user ────────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', password='admin123',
                email='admin@civic.local',
                first_name='Civic', last_name='Admin',
                role='admin',
            )
            self.stdout.write('  ✅  Admin user created  (admin / admin123)')
        else:
            self.stdout.write('  ⏭   Admin user already exists')

        # ── Citizen user ──────────────────────────────────────────────────
        citizen, created = User.objects.get_or_create(
            username='citizen1',
            defaults={
                'email': 'citizen@civic.local',
                'first_name': 'Ravi', 'last_name': 'Kumar',
                'role': 'citizen',
            }
        )
        if created:
            citizen.set_password('citizen123')
            citizen.save()
            self.stdout.write('  ✅  Citizen user created (citizen1 / citizen123)')

        # ── Sample complaints ──────────────────────────────────────────────
        sample = [
            {
                'title': 'Overflowing garbage bins near City Market',
                'description': 'The garbage bins on MG Road near City Market have been overflowing for 3 days. Strong odour and health hazard for nearby residents.',
                'category': cat_objects['Garbage'],
                'department': dept_objects['Sanitation & Waste'],
                'location_text': 'MG Road, City Market, Bengaluru, Karnataka',
                'latitude': 12.9716, 'longitude': 77.5946,
                'status': 'in_progress',
            },
            {
                'title': 'Large pothole on NH-48 causes accidents',
                'description': 'A 2-foot deep pothole near the toll plaza on NH-48 has caused 2 bike accidents this week. Urgent repair needed.',
                'category': cat_objects['Pothole / Road'],
                'department': dept_objects['Roads & Infrastructure'],
                'location_text': 'NH-48, Toll Plaza, Tumkur Road, Bengaluru',
                'latitude': 13.0068, 'longitude': 77.5484,
                'status': 'submitted',
            },
            {
                'title': 'Streetlight not working for 2 weeks',
                'description': 'The streetlight in front of House No. 45, 3rd Cross, Jayanagar has been non-functional for 2 weeks, making the area unsafe at night.',
                'category': cat_objects['Streetlight'],
                'department': dept_objects['Electricity Board'],
                'location_text': '3rd Cross, Jayanagar, Bengaluru, Karnataka',
                'latitude': 12.9250, 'longitude': 77.5938,
                'status': 'resolved',
            },
            {
                'title': 'Water pipe burst flooding the road',
                'description': 'A water supply pipe has burst at the junction of 5th Main and 1st Cross, Indiranagar. Water is flooding the road and entering homes.',
                'category': cat_objects['Water Leakage'],
                'department': dept_objects['Water Supply Board'],
                'location_text': '5th Main & 1st Cross, Indiranagar, Bengaluru',
                'latitude': 12.9784, 'longitude': 77.6408,
                'status': 'in_progress',
            },
            {
                'title': 'Storm drain blocked causing waterlogging',
                'description': 'The storm drain near the bus stop on Hosur Road is completely blocked with debris. Heavy rain causes the entire area to flood.',
                'category': cat_objects['Drainage'],
                'department': dept_objects['Storm Drain Division'],
                'location_text': 'Hosur Road, BTM Layout, Bengaluru, Karnataka',
                'latitude': 12.9165, 'longitude': 77.6101,
                'status': 'submitted',
            },
        ]

        created_count = 0
        for s in sample:
            if not Complaint.objects.filter(title=s['title']).exists():
                Complaint.objects.create(user=citizen, **s)
                created_count += 1

        self.stdout.write(f'  ✅  {created_count} sample complaints created')
        self.stdout.write(self.style.SUCCESS('\n🎉  Seed complete! Run: python manage.py runserver'))
        self.stdout.write('    Admin login  → http://127.0.0.1:8000/users/login/  (admin / admin123)')
        self.stdout.write('    Citizen login→ http://127.0.0.1:8000/users/login/  (citizen1 / citizen123)')
