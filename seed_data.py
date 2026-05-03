import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_project.settings')
django.setup()

from complaints.models import Category, Department

# Create Categories
categories = [
    {'name': 'Garbage Collection', 'icon': 'trash', 'color': '#ef4444'},
    {'name': 'Pothole & Roads', 'icon': 'road', 'color': '#f59e0b'},
    {'name': 'Streetlight Repair', 'icon': 'lightbulb', 'color': '#eab308'},
    {'name': 'Water Leakage', 'icon': 'droplet', 'color': '#3b82f6'},
    {'name': 'Drainage Issue', 'icon': 'water', 'color': '#06b6d4'},
    {'name': 'Other Repairs', 'icon': 'tools', 'color': '#6366f1'},
]

for cat_data in categories:
    cat, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
    if created:
        print(f"Created category: {cat.name}")

# Create Departments
departments = [
    {'name': 'Sanitation Department', 'email': 'sanitation@civic.local'},
    {'name': 'Roads & Public Works', 'email': 'roads@civic.local'},
    {'name': 'Electricity Board', 'email': 'power@civic.local'},
    {'name': 'Water Supply Board', 'email': 'water@civic.local'},
]

for dept_data in departments:
    dept, created = Department.objects.get_or_create(name=dept_data['name'], defaults=dept_data)
    if created:
        print(f"Created department: {dept.name}")
