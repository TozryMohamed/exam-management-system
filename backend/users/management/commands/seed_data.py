from django.core.management.base import BaseCommand
from users.models import Department, Groupe

class Command(BaseCommand):
    help = "Seed departments and groupes"

    def handle(self, *args, **kwargs):

        data = [
            {"code": "GLSI", "name": "Génie Logiciel", "groupes": 3},
            {"code": "ISI", "name": "Informatique Industrielle", "groupes": 3},
            {"code": "TIC", "name": "Télécom & Communication", "groupes": 3},
            {"code": "EEA", "name": "Électronique", "groupes": 3},
            {"code": "GM", "name": "Génie Mécanique", "groupes": 3},
        ]

        for d in data:
            dep, created = Department.objects.get_or_create(
                code=d["code"],
                defaults={"name": d["name"]}
            )

            for i in range(1, d["groupes"] + 1):
                Groupe.objects.get_or_create(
                    name=f"{d['code']} {i}",
                    department=dep,
                    level=i   # ✅ FIX
                )

        self.stdout.write(self.style.SUCCESS("✅ Seed completed"))