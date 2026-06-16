# groupes/management/commands/seed_groupes.py
from django.core.management.base import BaseCommand
from groupes.models import GroupeEtudiant
from matieres.models import Specialite

class Command(BaseCommand):
    help = "Seed groupes d'étudiants"

    def handle(self, *args, **kwargs):
        specialites = Specialite.objects.all()
        
        groupes_data = [
            # GLSI
            {'nom': 'GLSI 1', 'specialite_code': 'GLSI', 'effectif': 35, 'niveau': 'L3'},
            {'nom': 'GLSI 2', 'specialite_code': 'GLSI', 'effectif': 32, 'niveau': 'L3'},
            {'nom': 'GLSI 3', 'specialite_code': 'GLSI', 'effectif': 30, 'niveau': 'L3'},
            # ISI
            {'nom': 'ISI 1', 'specialite_code': 'ISI', 'effectif': 28, 'niveau': 'L3'},
            {'nom': 'ISI 2', 'specialite_code': 'ISI', 'effectif': 25, 'niveau': 'L3'},
            # TIC
            {'nom': 'TIC 1', 'specialite_code': 'TIC', 'effectif': 30, 'niveau': 'L3'},
            {'nom': 'TIC 2', 'specialite_code': 'TIC', 'effectif': 28, 'niveau': 'L3'},
            # EEA
            {'nom': 'EEA 1', 'specialite_code': 'EEA', 'effectif': 25, 'niveau': 'L3'},
            # GM
            {'nom': 'GM 1', 'specialite_code': 'GM', 'effectif': 22, 'niveau': 'L3'},
        ]
        
        for data in groupes_data:
            specialite = Specialite.objects.get(code=data['specialite_code'])
            GroupeEtudiant.objects.create(
                nom=data['nom'],
                specialite=specialite,
                effectif=data['effectif'],
                niveau=data['niveau']
            )
            self.stdout.write(f"✅ Groupe créé: {data['nom']}")
        
        self.stdout.write(self.style.SUCCESS("🎉 Seed des groupes terminé!"))