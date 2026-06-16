from django.core.management.base import BaseCommand
from exams.models import Salle

class Command(BaseCommand):
    help = "Seed salles and amphis"

    def handle(self, *args, **kwargs):

        # 🧹 تنظيف (اختياري)
        Salle.objects.all().delete()

        # 🏫 salles 1 → 26
        for i in range(1, 27):
            Salle.objects.create(
                name=str(i),
                capacity=30,
                type="salle"
            )

        # 🎓 amphis 1 → 5
        for i in range(1, 6):
            Salle.objects.create(
                name=str(i),
                capacity=200,
                type="amphi"
            )

        self.stdout.write(self.style.SUCCESS("✅ Seed done"))