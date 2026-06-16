# clean_tables.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.db import connection

print("Nettoyage des tables groupes...")

with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS groups_placementhistorique")
    print("1. groups_placementhistorique supprimee")
    
    cursor.execute("DROP TABLE IF EXISTS groups_regroupementhistorique")
    print("2. groups_regroupementhistorique supprimee")
    
    cursor.execute("DROP TABLE IF EXISTS groups_regroupementhistorique_examens_concerenes")
    print("3. groups_regroupementhistorique_examens_concerenes supprimee")

print("\nSuppression terminee!")

with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'groups_%' ORDER BY name")
    tables = cursor.fetchall()
    print("\nTables groupes restantes:")
    for table in tables:
        print(f"  - {table[0]}")