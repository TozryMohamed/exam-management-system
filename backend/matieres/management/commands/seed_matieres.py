# # matieres/management/commands/seed_data.py
# from django.core.management.base import BaseCommand
# from matieres.models import Specialite, Matiere  # ← CHANGÉ: exams.models → matieres.models

# class Command(BaseCommand):
#     help = "Seed specialites and matieres"

#     def handle(self, *args, **kwargs):
#         self.stdout.write("🚀 Début du seeding des matières...")
        
#         # Supprimer les données existantes
#         Specialite.objects.all().delete()
#         self.stdout.write("🗑 Anciennes données supprimées")
        
#         # Données des spécialités
#         specialites_data = {
#             'GLSI': {
#                 'nom': 'Génie Logiciel & Systèmes d\'Information',
#                 'description': 'Spécialité axée sur le développement logiciel et les systèmes d\'information',
#                 'matieres': [
#                     ('ALG101', 'Algorithmique et programmation 1', 3, 2, 'MX', 1),
#                     ('ALG102', 'Algorithmique et structure de données', 3, 2, 'MX', 1),
#                     ('ATP101', 'Atelier programmation 1', 2, 1, 'TP', 1),
#                     ('MATH101', 'Analyse 1', 3, 2, 'MX', 1),
#                     ('MATH102', 'Algèbre 1', 3, 2, 'MX', 1),
#                     ('LGM101', 'Technologies multimédias', 2, 1, 'MX', 1),
#                     ('LGM102', 'Logique formelle', 2, 1, 'MX', 1),
#                     ('SEA101', 'Système d’exploitation 1', 3, 2, 'MX', 1),
#                     ('SEA102', 'Systèmes logiques et architecture des ordinateurs', 3, 2, 'MX', 1),
#                     ('ALG201', 'Programmation Python', 3, 2, 'MX', 2),
#                     ('ALG202', 'Algorithmique, structure de données et complexité', 3, 2, 'MX', 2),
#                     ('ATP201', 'Atelier de programmation 2', 2, 1, 'TP', 2),
#                     ('BD201', 'Fondements des bases de données', 3, 2, 'MX', 2),
#                     ('BD202', 'Fondements des réseaux', 3, 2, 'MX', 2),
#                     ('PROB201', 'Probabilité et statistique', 3, 2, 'MX', 2),
#                     ('CPOO301', 'Conception des systèmes d’information', 3, 2, 'MX', 3),
#                     ('CPOO302', 'Programmation Java', 3, 2, 'TP', 3),
#                     ('AUTO301', 'Graphes et optimisation', 3, 2, 'MX', 3),
#                     ('AUTO302', 'Théorie des automates', 3, 2, 'MX', 3),
#                     ('BDR401', 'Ingénierie des bases de données', 3, 2, 'MX', 4),
#                     ('BDR402', 'Services des réseaux', 3, 2, 'MX', 4),
#                     ('COM401', 'Techniques de compilation', 3, 2, 'MX', 4),
#                     ('COM402', 'Tests de logiciels', 2, 1, 'TP', 4),
#                     ('WEB501', 'Technologies web', 3, 2, 'TP', 5),
#                     ('IA501', 'Fondements de l’intelligence artificielle', 3, 2, 'MX', 5),
#                     ('CLOUD501', 'Virtualisation et Cloud', 3, 2, 'MX', 5),
#                     ('CLOUD502', 'Big Data', 3, 2, 'MX', 5),
#                     ('DEV601', 'Développement d’applications réparties', 3, 2, 'MX', 6),
#                     ('DEV602', 'Développement Mobile', 3, 2, 'TP', 6),
#                     ('ML601', 'Machine Learning', 3, 2, 'MX', 6),
#                     ('SEC601', 'Sécurité informatique', 3, 2, 'MX', 6),
#                     ('SOA601', 'Architecture SOA et services Web', 3, 2, 'MX', 6),
#                     ('PFE601', 'Projet de Fin d\'Études', 10, 6, 'MX', 6),
#                 ]
#             },
#             'ISI': {
#                 'nom': 'Informatique des Systèmes Industriels',
#                 'description': 'Spécialité orientée systèmes embarqués et informatique industrielle',
#                 'matieres': [
#                     ('SE101', 'Microcontrôleurs', 3, 2, 'MX', 1),
#                     ('SE102', 'Programmation embarquée', 3, 2, 'TP', 1),
#                     ('SE103', 'Architecture des systèmes', 3, 2, 'MX', 1),
#                     ('AUTO101', 'Asservissement', 3, 2, 'MX', 2),
#                     ('AUTO102', 'Commande des systèmes', 3, 2, 'MX', 2),
#                     ('AUTO103', 'Automatique continue', 3, 2, 'MX', 2),
#                     ('II201', 'SCADA', 3, 2, 'MX', 3),
#                     ('II202', 'API (Automates programmables)', 3, 2, 'TP', 3),
#                     ('RI301', 'Bus de terrain', 3, 2, 'MX', 4),
#                     ('RI302', 'Protocoles industriels', 3, 2, 'MX', 4),
#                     ('EN401', 'Logique séquentielle', 3, 2, 'MX', 5),
#                     ('EN402', 'FPGA', 3, 2, 'TP', 5),
#                 ]
#             },
#             'TIC': {
#                 'nom': 'Technologies de l\'Information et Communication',
#                 'description': 'Spécialité réseaux, télécommunications et développement web',
#                 'matieres': [
#                     ('RES101', 'Réseaux 1', 3, 2, 'MX', 1),
#                     ('RES102', 'Réseaux 2', 3, 2, 'MX', 2),
#                     ('RES103', 'Administration réseau', 3, 2, 'TP', 3),
#                     ('TEL101', 'Transmission de données', 3, 2, 'MX', 1),
#                     ('TEL102', 'Signal analogique et numérique', 3, 2, 'MX', 2),
#                     ('WEB101', 'HTML/CSS', 2, 1, 'TP', 1),
#                     ('WEB102', 'JavaScript', 2, 1, 'TP', 2),
#                     ('WEB103', 'Framework Web', 3, 2, 'TP', 3),
#                     ('SEC101', 'Cryptographie', 3, 2, 'MX', 4),
#                     ('SEC102', 'Sécurité réseau', 3, 2, 'MX', 5),
#                 ]
#             },
#             'EEA': {
#                 'nom': 'Electronique, Electrotechnique, Automatique',
#                 'description': 'Spécialité électronique et automatique',
#                 'matieres': [
#                     ('EA101', 'Amplificateurs', 3, 2, 'MX', 1),
#                     ('EA102', 'Circuits analogiques', 3, 2, 'MX', 1),
#                     ('EN101', 'Logique combinatoire', 3, 2, 'MX', 2),
#                     ('EN102', 'Microprocesseurs', 3, 2, 'MX', 2),
#                     ('EL101', 'Circuits électriques', 3, 2, 'MX', 1),
#                     ('EL102', 'Analyse des réseaux', 3, 2, 'MX', 2),
#                     ('AUTO201', 'Systèmes asservis', 3, 2, 'MX', 3),
#                     ('AUTO202', 'Commande', 3, 2, 'MX', 4),
#                 ]
#             },
#             'GM': {
#                 'nom': 'Génie Mécanique',
#                 'description': 'Spécialité mécanique et conception',
#                 'matieres': [
#                     ('MEC101', 'Cinématique', 3, 2, 'MX', 1),
#                     ('MEC102', 'Dynamique', 3, 2, 'MX', 1),
#                     ('RDM101', 'Contraintes', 3, 2, 'MX', 2),
#                     ('RDM102', 'Déformations', 3, 2, 'MX', 2),
#                     ('CM101', 'Dessin industriel', 3, 2, 'TP', 1),
#                     ('CM102', 'Dimensionnement', 3, 2, 'MX', 2),
#                     ('TH101', 'Lois thermodynamiques', 3, 2, 'MX', 3),
#                     ('TH102', 'Machines thermiques', 3, 2, 'MX', 4),
#                 ]
#             }
#         }
        
#         # Création des spécialités et matières
#         for code, data in specialites_data.items():
#             specialite = Specialite.objects.create(
#                 code=code,
#                 nom=data['nom'],
#                 description=data['description']
#             )
#             self.stdout.write(f"✅ Spécialité créée: {code}")
            
#             for matiere_data in data['matieres']:
#                 code_matiere, titre, credits, coefficient, nature, semestre = matiere_data
#                 Matiere.objects.create(
#                     code=code_matiere,
#                     titre=titre,
#                     credits=credits,
#                     coefficient=coefficient,
#                     nature=nature,
#                     specialite=specialite,
#                     semestre=semestre
#                 )
#                 self.stdout.write(f"  📚 Ajouté: {code_matiere} - {titre}")
        
#         # Statistiques
#         total_specialites = Specialite.objects.count()
#         total_matieres = Matiere.objects.count()
        
#         self.stdout.write(self.style.SUCCESS(f"\n🎉 Seed terminé avec succès!"))
#         self.stdout.write(self.style.SUCCESS(f"📊 {total_specialites} spécialités créées"))
#         self.stdout.write(self.style.SUCCESS(f"📚 {total_matieres} matières créées"))









from django.core.management.base import BaseCommand
from matieres.models import Specialite, Matiere
from users.models import Department


class Command(BaseCommand):
    help = "Seed des spécialités et matières avec niveaux"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Début du seeding des matières avec niveaux...")
        
        Matiere.objects.all().delete()
        Specialite.objects.all().delete()
        self.stdout.write("🗑 Anciennes données supprimées")
        
        departments = {
            code: Department.objects.get_or_create(
                code=code, 
                defaults={'name': name}
            )[0]
            for code, name in [
                ('GLSI', 'Génie Logiciel et Systèmes d\'Information'),
                ('ISI', 'Informatique des Systèmes Industriels'),
                ('TIC', 'Technologies de l\'Information et Communication'),
                ('EEA', 'Électronique, Électrotechnique et Automatique'),
                ('GM', 'Génie Mécanique'),
            ]
        }
        
        specialites_config = {
            'GLSI': {
                'nom': 'Génie Logiciel & Systèmes d\'Information',
                'description': 'Formation en développement logiciel et systèmes d\'information',
                'matieres': [
                    ('ALG101', 'Algorithmique et programmation 1', 3, 2, 'MX', 1, 1),
                    ('ALG102', 'Algorithmique et structure de données', 3, 2, 'MX', 1, 1),
                    ('ATP101', 'Atelier programmation 1', 2, 1, 'TP', 1, 1),
                    ('MATH101', 'Analyse 1', 3, 2, 'MX', 1, 1),
                    ('MATH102', 'Algèbre 1', 3, 2, 'MX', 1, 1),
                    ('LGM101', 'Technologies multimédias', 2, 1, 'MX', 1, 1),
                    ('LGM102', 'Logique formelle', 2, 1, 'MX', 1, 1),
                    ('SEA101', 'Système d\'exploitation 1', 3, 2, 'MX', 1, 1),
                    ('SEA102', 'Architecture des ordinateurs', 3, 2, 'MX', 1, 1),
                    ('ALG201', 'Programmation Python', 3, 2, 'MX', 3, 2),
                    ('ALG202', 'Algorithmique avancée', 3, 2, 'MX', 3, 2),
                    ('ATP201', 'Atelier de programmation 2', 2, 1, 'TP', 3, 2),
                    ('BD201', 'Fondements des bases de données', 3, 2, 'MX', 3, 2),
                    ('BD202', 'Fondements des réseaux', 3, 2, 'MX', 3, 2),
                    ('PROB201', 'Probabilité et statistique', 3, 2, 'MX', 3, 2),
                    ('AUTO301', 'Graphes et optimisation', 3, 2, 'MX', 4, 2),
                    ('AUTO302', 'Théorie des automates', 3, 2, 'MX', 4, 2),
                    ('CPOO301', 'Conception des SI', 3, 2, 'MX', 5, 3),
                    ('CPOO302', 'Programmation Java', 3, 2, 'TP', 5, 3),
                    ('BDR401', 'Ingénierie des bases de données', 3, 2, 'MX', 5, 3),
                    ('BDR402', 'Services des réseaux', 3, 2, 'MX', 5, 3),
                    ('WEB501', 'Technologies web', 3, 2, 'TP', 5, 3),
                    ('IA501', 'Intelligence artificielle', 3, 2, 'MX', 6, 3),
                    ('CLOUD501', 'Virtualisation et Cloud', 3, 2, 'MX', 6, 3),
                    ('CLOUD502', 'Big Data', 3, 2, 'MX', 6, 3),
                    ('DEV601', 'Applications réparties', 3, 2, 'MX', 6, 3),
                    ('DEV602', 'Développement Mobile', 3, 2, 'TP', 6, 3),
                    ('ML601', 'Machine Learning', 3, 2, 'MX', 6, 3),
                    ('SEC601', 'Sécurité informatique', 3, 2, 'MX', 6, 3),
                    ('SOA601', 'Architecture SOA', 3, 2, 'MX', 6, 3),
                    ('PFE601', 'Projet de Fin d\'Études', 10, 6, 'MX', 6, 3),
                    # Niveau 1 — Semestre 1 (nouveaux)
                    ('GLSX101', 'Introduction au génie logiciel', 2, 1, 'MX', 1, 1),
                    ('GLSX102', 'Outils de développement et versioning', 2, 1, 'TP', 1, 1),
                    ('GLSX103', 'Mathématiques discrètes', 3, 2, 'MX', 1, 1),
                    ('GLSX104', 'Communication technique et rédaction', 1, 1, 'MX', 1, 1),
                    ('GLSX105', 'Introduction à la cybersécurité', 2, 1, 'MX', 1, 1),
                    # Niveau 1 — Semestre 2 (nouveaux)
                    ('GLSX106', 'Programmation C avancée', 3, 2, 'TP', 2, 1),
                    ('GLSX107', 'Systèmes d\'exploitation 2', 3, 2, 'MX', 2, 1),
                    ('GLSX108', 'Algèbre linéaire appliquée', 3, 2, 'MX', 2, 1),
                    ('GLSX109', 'Introduction aux bases de données', 2, 1, 'MX', 2, 1),
                    ('GLSX110', 'Atelier systèmes Linux', 2, 1, 'TP', 2, 1),
                    ('GLSX111', 'Anglais technique 1', 1, 1, 'MX', 2, 1),
                    # Niveau 2 — Semestre 3 (nouveaux)
                    ('GLSX201', 'Programmation orientée objet avancée', 3, 2, 'MX', 3, 2),
                    ('GLSX202', 'Conception UML', 3, 2, 'MX', 3, 2),
                    ('GLSX203', 'Développement web front-end', 3, 2, 'TP', 3, 2),
                    ('GLSX204', 'Administration des bases de données', 3, 2, 'MX', 3, 2),
                    ('GLSX205', 'Sécurité des systèmes d\'information', 2, 1, 'MX', 3, 2),
                    ('GLSX206', 'Mathématiques pour l\'IA', 3, 2, 'MX', 3, 2),
                    # Niveau 2 — Semestre 4 (nouveaux)
                    ('GLSX207', 'Design Patterns', 3, 2, 'MX', 4, 2),
                    ('GLSX208', 'Développement web back-end', 3, 2, 'TP', 4, 2),
                    ('GLSX209', 'Base de données NoSQL', 3, 2, 'MX', 4, 2),
                    ('GLSX210', 'Protocoles réseaux avancés', 3, 2, 'MX', 4, 2),
                    ('GLSX211', 'Test et qualité logicielle', 2, 1, 'MX', 4, 2),
                    ('GLSX212', 'Anglais technique 2', 1, 1, 'MX', 4, 2),
                    ('GLSX213', 'Stage niveau 2', 4, 2, 'TP', 4, 2),
                    # Niveau 3 — Semestre 5 (nouveaux)
                    ('GLSX301', 'Architecture microservices', 3, 2, 'MX', 5, 3),
                    ('GLSX302', 'DevOps et CI/CD', 3, 2, 'TP', 5, 3),
                    ('GLSX303', 'Data Science et visualisation', 3, 2, 'MX', 5, 3),
                    ('GLSX304', 'Développement mobile avancé (Flutter)', 3, 2, 'TP', 5, 3),
                    ('GLSX305', 'Cloud Computing AWS/Azure', 3, 2, 'MX', 5, 3),
                    ('GLSX306', 'Gestion de projet agile (Scrum/Kanban)', 2, 1, 'MX', 5, 3),
                    ('GLSX307', 'API REST et GraphQL', 3, 2, 'TP', 5, 3),
                    # Niveau 3 — Semestre 6 (nouveaux)
                    ('GLSX308', 'Deep Learning', 3, 2, 'MX', 6, 3),
                    ('GLSX309', 'Blockchain et contrats intelligents', 3, 2, 'MX', 6, 3),
                    ('GLSX310', 'Cybersécurité avancée', 3, 2, 'MX', 6, 3),
                    ('GLSX311', 'Conteneurisation et Kubernetes', 3, 2, 'TP', 6, 3),
                    ('GLSX312', 'Traitement du langage naturel (NLP)', 3, 2, 'MX', 6, 3),
                    ('GLSX313', 'IoT et systèmes connectés', 2, 1, 'MX', 6, 3),
                    ('GLSX314', 'Entrepreneuriat et innovation technologique', 2, 1, 'MX', 6, 3),
                ]
            },
            'ISI': {
                'nom': 'Informatique des Systèmes Industriels',
                'description': 'Systèmes embarqués et informatique industrielle',
                'matieres': [
                    ('SE101', 'Microcontrôleurs', 3, 2, 'MX', 1, 1),
                    ('SE102', 'Programmation embarquée', 3, 2, 'TP', 1, 1),
                    ('SE103', 'Architecture des systèmes', 3, 2, 'MX', 1, 1),
                    ('AUTO101', 'Asservissement', 3, 2, 'MX', 2, 1),
                    ('AUTO102', 'Commande des systèmes', 3, 2, 'MX', 2, 1),
                    ('AUTO103', 'Automatique continue', 3, 2, 'MX', 3, 2),
                    ('II201', 'SCADA', 3, 2, 'MX', 3, 2),
                    ('II202', 'API (Automates)', 3, 2, 'TP', 4, 2),
                    ('RI301', 'Bus de terrain', 3, 2, 'MX', 5, 3),
                    ('RI302', 'Protocoles industriels', 3, 2, 'MX', 5, 3),
                    ('EN401', 'Logique séquentielle', 3, 2, 'MX', 6, 3),
                    ('EN402', 'FPGA', 3, 2, 'TP', 6, 3),
                    # Niveau 1 — Semestre 1 (nouveaux)
                    ('ISIX101', 'Mathématiques pour l\'ingénieur 1', 3, 2, 'MX', 1, 1),
                    ('ISIX102', 'Electronique de base', 3, 2, 'MX', 1, 1),
                    ('ISIX103', 'Algorithmique et C embarqué', 3, 2, 'TP', 1, 1),
                    ('ISIX104', 'Capteurs et actionneurs', 2, 1, 'MX', 1, 1),
                    ('ISIX105', 'Introduction aux systèmes temps réel', 2, 1, 'MX', 1, 1),
                    # Niveau 1 — Semestre 2 (nouveaux)
                    ('ISIX106', 'Systèmes d\'exploitation temps réel (RTOS)', 3, 2, 'MX', 2, 1),
                    ('ISIX107', 'Programmation C++ pour systèmes embarqués', 3, 2, 'TP', 2, 1),
                    ('ISIX108', 'Mathématiques pour l\'ingénieur 2', 3, 2, 'MX', 2, 1),
                    ('ISIX109', 'Réseaux industriels de base', 2, 1, 'MX', 2, 1),
                    ('ISIX110', 'Atelier microcontrôleurs Arduino/STM32', 2, 1, 'TP', 2, 1),
                    # Niveau 2 — Semestre 3 (nouveaux)
                    ('ISIX201', 'Systèmes embarqués Linux', 3, 2, 'MX', 3, 2),
                    ('ISIX202', 'Communication série et sans fil (UART, SPI, I2C, BLE)', 3, 2, 'TP', 3, 2),
                    ('ISIX203', 'Automatique discrète', 3, 2, 'MX', 3, 2),
                    ('ISIX204', 'Traitement du signal numérique', 3, 2, 'MX', 3, 2),
                    ('ISIX205', 'Cybersécurité des systèmes industriels', 2, 1, 'MX', 3, 2),
                    # Niveau 2 — Semestre 4 (nouveaux)
                    ('ISIX206', 'Intelligence artificielle embarquée', 3, 2, 'MX', 4, 2),
                    ('ISIX207', 'Vision par ordinateur industrielle', 3, 2, 'TP', 4, 2),
                    ('ISIX208', 'Maintenance prédictive et IoT industriel', 3, 2, 'MX', 4, 2),
                    ('ISIX209', 'Réseaux industriels avancés (Profibus, Modbus)', 3, 2, 'MX', 4, 2),
                    ('ISIX210', 'Stage niveau 2', 4, 2, 'TP', 4, 2),
                    # Niveau 3 — Semestre 5 (nouveaux)
                    ('ISIX301', 'Machine Learning pour systèmes industriels', 3, 2, 'MX', 5, 3),
                    ('ISIX302', 'Industrie 4.0 et usine numérique', 3, 2, 'MX', 5, 3),
                    ('ISIX303', 'Digital Twin et simulation industrielle', 3, 2, 'MX', 5, 3),
                    ('ISIX304', 'Cloud industriel et Edge Computing', 3, 2, 'MX', 5, 3),
                    ('ISIX305', 'Robotique et systèmes autonomes', 3, 2, 'TP', 5, 3),
                    ('ISIX306', 'Gestion de projet industriel', 2, 1, 'MX', 5, 3),
                    # Niveau 3 — Semestre 6 (nouveaux)
                    ('ISIX307', 'Big Data industriel', 3, 2, 'MX', 6, 3),
                    ('ISIX308', 'Sécurité fonctionnelle (IEC 61508)', 3, 2, 'MX', 6, 3),
                    ('ISIX309', 'Développement d\'applications SCADA avancées', 3, 2, 'TP', 6, 3),
                    ('ISIX310', 'Blockchain pour la traçabilité industrielle', 2, 1, 'MX', 6, 3),
                    ('ISIX311', 'Projet de Fin d\'Études', 10, 6, 'MX', 6, 3),
                ]
            },
            'TIC': {
                'nom': 'Technologies de l\'Information et Communication',
                'description': 'Réseaux, télécommunications et développement web',
                'matieres': [
                    ('RES101', 'Réseaux 1', 3, 2, 'MX', 1, 1),
                    ('TEL101', 'Transmission de données', 3, 2, 'MX', 1, 1),
                    ('WEB101', 'HTML/CSS', 2, 1, 'TP', 1, 1),
                    ('RES102', 'Réseaux 2', 3, 2, 'MX', 3, 2),
                    ('TEL102', 'Signal analogique', 3, 2, 'MX', 3, 2),
                    ('WEB102', 'JavaScript', 2, 1, 'TP', 4, 2),
                    ('WEB103', 'Framework Web', 3, 2, 'TP', 4, 2),
                    ('RES103', 'Administration réseau', 3, 2, 'TP', 5, 3),
                    ('SEC101', 'Cryptographie', 3, 2, 'MX', 5, 3),
                    ('SEC102', 'Sécurité réseau', 3, 2, 'MX', 6, 3),
                    # Niveau 1 — Semestre 1 (nouveaux)
                    ('TICX101', 'Algorithmique et programmation', 3, 2, 'MX', 1, 1),
                    ('TICX102', 'Mathématiques pour les télécoms 1', 3, 2, 'MX', 1, 1),
                    ('TICX103', 'Systèmes d\'exploitation', 2, 1, 'MX', 1, 1),
                    ('TICX104', 'Introduction aux télécommunications', 2, 1, 'MX', 1, 1),
                    ('TICX105', 'Atelier câblage et infrastructure réseau', 2, 1, 'TP', 1, 1),
                    # Niveau 1 — Semestre 2 (nouveaux)
                    ('TICX106', 'Mathématiques pour les télécoms 2', 3, 2, 'MX', 2, 1),
                    ('TICX107', 'Programmation Python pour réseaux', 3, 2, 'TP', 2, 1),
                    ('TICX108', 'Modèle OSI et protocoles fondamentaux', 3, 2, 'MX', 2, 1),
                    ('TICX109', 'Introduction à la virtualisation', 2, 1, 'MX', 2, 1),
                    ('TICX110', 'Anglais des télécommunications', 1, 1, 'MX', 2, 1),
                    # Niveau 2 — Semestre 3 (nouveaux)
                    ('TICX201', 'Routage et commutation (CCNA niveau 1)', 3, 2, 'MX', 3, 2),
                    ('TICX202', 'Développement web full-stack', 3, 2, 'TP', 3, 2),
                    ('TICX203', 'Bases de données pour réseaux', 3, 2, 'MX', 3, 2),
                    ('TICX204', 'Réseaux mobiles 4G/5G', 3, 2, 'MX', 3, 2),
                    ('TICX205', 'Cybersécurité fondamentale', 2, 1, 'MX', 3, 2),
                    # Niveau 2 — Semestre 4 (nouveaux)
                    ('TICX206', 'Routage et commutation avancés (CCNA niveau 2)', 3, 2, 'MX', 4, 2),
                    ('TICX207', 'VoIP et télécommunications unifiées', 3, 2, 'MX', 4, 2),
                    ('TICX208', 'Cloud et virtualisation réseau (SDN/NFV)', 3, 2, 'MX', 4, 2),
                    ('TICX209', 'Développement d\'applications mobiles', 3, 2, 'TP', 4, 2),
                    ('TICX210', 'Gestion de projet en télécommunications', 2, 1, 'MX', 4, 2),
                    ('TICX211', 'Stage niveau 2', 4, 2, 'TP', 4, 2),
                    # Niveau 3 — Semestre 5 (nouveaux)
                    ('TICX301', 'Sécurité réseau avancée et pentesting', 3, 2, 'MX', 5, 3),
                    ('TICX302', 'Big Data et analytique réseau', 3, 2, 'MX', 5, 3),
                    ('TICX303', 'IoT et protocoles M2M', 3, 2, 'MX', 5, 3),
                    ('TICX304', 'DevOps pour l\'infrastructure réseau', 3, 2, 'TP', 5, 3),
                    ('TICX305', 'Intelligence artificielle pour réseaux', 3, 2, 'MX', 5, 3),
                    ('TICX306', 'Fibre optique et réseaux très haut débit', 3, 2, 'MX', 5, 3),
                    # Niveau 3 — Semestre 6 (nouveaux)
                    ('TICX307', 'Blockchain et applications décentralisées', 3, 2, 'MX', 6, 3),
                    ('TICX308', 'Edge Computing et Fog Computing', 3, 2, 'MX', 6, 3),
                    ('TICX309', 'Administration cloud (AWS/Azure/GCP)', 3, 2, 'TP', 6, 3),
                    ('TICX310', 'Cybersécurité et conformité (ISO 27001)', 3, 2, 'MX', 6, 3),
                    ('TICX311', 'Entrepreneuriat numérique', 2, 1, 'MX', 6, 3),
                    ('TICX312', 'Projet de Fin d\'Études', 10, 6, 'MX', 6, 3),
                ]
            },
            'EEA': {
                'nom': 'Électronique, Électrotechnique, Automatique',
                'description': 'Électronique et automatique',
                'matieres': [
                    ('EA101', 'Amplificateurs', 3, 2, 'MX', 1, 1),
                    ('EA102', 'Circuits analogiques', 3, 2, 'MX', 1, 1),
                    ('EL101', 'Circuits électriques', 3, 2, 'MX', 1, 1),
                    ('EN101', 'Logique combinatoire', 3, 2, 'MX', 3, 2),
                    ('EN102', 'Microprocesseurs', 3, 2, 'MX', 3, 2),
                    ('EL102', 'Analyse des réseaux', 3, 2, 'MX', 4, 2),
                    ('AUTO201', 'Systèmes asservis', 3, 2, 'MX', 5, 3),
                    ('AUTO202', 'Commande avancée', 3, 2, 'MX', 6, 3),
                    # Niveau 1 — Semestre 1 (nouveaux)
                    ('EEAX101', 'Mathématiques pour l\'électronique 1', 3, 2, 'MX', 1, 1),
                    ('EEAX102', 'Physique des composants électroniques', 3, 2, 'MX', 1, 1),
                    ('EEAX103', 'Programmation C pour électroniciens', 2, 1, 'TP', 1, 1),
                    ('EEAX104', 'Introduction à l\'électrotechnique', 3, 2, 'MX', 1, 1),
                    ('EEAX105', 'Atelier mesures électriques', 2, 1, 'TP', 1, 1),
                    # Niveau 1 — Semestre 2 (nouveaux)
                    ('EEAX106', 'Mathématiques pour l\'électronique 2', 3, 2, 'MX', 2, 1),
                    ('EEAX107', 'Electronique de puissance 1', 3, 2, 'MX', 2, 1),
                    ('EEAX108', 'Filtrage et traitement du signal', 3, 2, 'MX', 2, 1),
                    ('EEAX109', 'Machines électriques 1', 3, 2, 'MX', 2, 1),
                    ('EEAX110', 'Atelier simulation électronique (LTSpice)', 2, 1, 'TP', 2, 1),
                    # Niveau 2 — Semestre 3 (nouveaux)
                    ('EEAX201', 'Electronique de puissance 2', 3, 2, 'MX', 3, 2),
                    ('EEAX202', 'Traitement numérique du signal (DSP)', 3, 2, 'MX', 3, 2),
                    ('EEAX203', 'Automatique avancée', 3, 2, 'MX', 3, 2),
                    ('EEAX204', 'Machines électriques 2', 3, 2, 'MX', 3, 2),
                    ('EEAX205', 'Systèmes embarqués pour l\'électronique', 3, 2, 'TP', 3, 2),
                    # Niveau 2 — Semestre 4 (nouveaux)
                    ('EEAX206', 'Variateurs de vitesse et entraînements', 3, 2, 'MX', 4, 2),
                    ('EEAX207', 'Commande des machines électriques', 3, 2, 'MX', 4, 2),
                    ('EEAX208', 'Energies renouvelables et systèmes photovoltaïques', 3, 2, 'MX', 4, 2),
                    ('EEAX209', 'Conception de circuits imprimés (PCB)', 3, 2, 'TP', 4, 2),
                    ('EEAX210', 'Stage niveau 2', 4, 2, 'TP', 4, 2),
                    # Niveau 3 — Semestre 5 (nouveaux)
                    ('EEAX301', 'Intelligence artificielle pour l\'automatique', 3, 2, 'MX', 5, 3),
                    ('EEAX302', 'IoT et systèmes électroniques connectés', 3, 2, 'MX', 5, 3),
                    ('EEAX303', 'Commande prédictive (MPC)', 3, 2, 'MX', 5, 3),
                    ('EEAX304', 'Simulation et jumeau numérique', 3, 2, 'TP', 5, 3),
                    ('EEAX305', 'Réseaux électriques intelligents (Smart Grid)', 3, 2, 'MX', 5, 3),
                    ('EEAX306', 'Conception VLSI et ASIC', 3, 2, 'MX', 5, 3),
                    # Niveau 3 — Semestre 6 (nouveaux)
                    ('EEAX307', 'Véhicules électriques et systèmes hybrides', 3, 2, 'MX', 6, 3),
                    ('EEAX308', 'Machine Learning pour le diagnostic industriel', 3, 2, 'MX', 6, 3),
                    ('EEAX309', 'Cybersécurité des systèmes électroniques', 2, 1, 'MX', 6, 3),
                    ('EEAX310', 'Stockage d\'énergie et piles à combustible', 3, 2, 'MX', 6, 3),
                    ('EEAX311', 'Gestion de projet et normes industrielles', 2, 1, 'MX', 6, 3),
                    ('EEAX312', 'Projet de Fin d\'Études', 10, 6, 'MX', 6, 3),
                ]
            },
            'GM': {
                'nom': 'Génie Mécanique',
                'description': 'Mécanique et conception industrielle',
                'matieres': [
                    ('MEC101', 'Cinématique', 3, 2, 'MX', 1, 1),
                    ('CM101', 'Dessin industriel', 3, 2, 'TP', 1, 1),
                    ('TH101', 'Lois thermodynamiques', 3, 2, 'MX', 1, 1),
                    ('MEC102', 'Dynamique', 3, 2, 'MX', 3, 2),
                    ('RDM101', 'Contraintes', 3, 2, 'MX', 3, 2),
                    ('RDM102', 'Déformations', 3, 2, 'MX', 4, 2),
                    ('CM102', 'Dimensionnement', 3, 2, 'MX', 4, 2),
                    ('TH102', 'Machines thermiques', 3, 2, 'MX', 6, 3),
                    # Niveau 1 — Semestre 1 (nouveaux)
                    ('GMX101', 'Mathématiques pour l\'ingénieur mécanique 1', 3, 2, 'MX', 1, 1),
                    ('GMX102', 'Physique mécanique', 3, 2, 'MX', 1, 1),
                    ('GMX103', 'Introduction à la CAO (SolidWorks)', 2, 1, 'TP', 1, 1),
                    ('GMX104', 'Matériaux et propriétés mécaniques', 3, 2, 'MX', 1, 1),
                    ('GMX105', 'Atelier fabrication et usinage 1', 2, 1, 'TP', 1, 1),
                    # Niveau 1 — Semestre 2 (nouveaux)
                    ('GMX106', 'Mathématiques pour l\'ingénieur mécanique 2', 3, 2, 'MX', 2, 1),
                    ('GMX107', 'Statique et équilibre des structures', 3, 2, 'MX', 2, 1),
                    ('GMX108', 'Mécanique des fluides 1', 3, 2, 'MX', 2, 1),
                    ('GMX109', 'Dessin assisté par ordinateur 2D/3D', 3, 2, 'TP', 2, 1),
                    ('GMX110', 'Atelier fabrication et usinage 2', 2, 1, 'TP', 2, 1),
                    ('GMX111', 'Anglais technique', 1, 1, 'MX', 2, 1),
                    # Niveau 2 — Semestre 3 (nouveaux)
                    ('GMX201', 'Résistance des matériaux avancée', 3, 2, 'MX', 3, 2),
                    ('GMX202', 'Méthode des éléments finis (FEM)', 3, 2, 'MX', 3, 2),
                    ('GMX203', 'Mécanique des fluides 2', 3, 2, 'MX', 3, 2),
                    ('GMX204', 'Transferts thermiques', 3, 2, 'MX', 3, 2),
                    ('GMX205', 'Conception mécanique avancée (CAO)', 3, 2, 'TP', 3, 2),
                    # Niveau 2 — Semestre 4 (nouveaux)
                    ('GMX206', 'Fabrication assistée par ordinateur (FAO)', 3, 2, 'TP', 4, 2),
                    ('GMX207', 'Mécatronique', 3, 2, 'MX', 4, 2),
                    ('GMX208', 'Gestion de production et méthodes industrielles', 3, 2, 'MX', 4, 2),
                    ('GMX209', 'Vibrations et acoustique industrielle', 3, 2, 'MX', 4, 2),
                    ('GMX210', 'Simulation numérique (ANSYS/MATLAB)', 3, 2, 'TP', 4, 2),
                    ('GMX211', 'Stage niveau 2', 4, 2, 'TP', 4, 2),
                    # Niveau 3 — Semestre 5 (nouveaux)
                    ('GMX301', 'Optimisation topologique et conception légère', 3, 2, 'MX', 5, 3),
                    ('GMX302', 'Fabrication additive et impression 3D', 3, 2, 'TP', 5, 3),
                    ('GMX303', 'Maintenance industrielle et fiabilité', 3, 2, 'MX', 5, 3),
                    ('GMX304', 'Hydraulique et pneumatique industrielles', 3, 2, 'MX', 5, 3),
                    ('GMX305', 'Jumeaux numériques et simulation avancée', 3, 2, 'MX', 5, 3),
                    ('GMX306', 'Gestion de projet industriel (MS Project)', 2, 1, 'MX', 5, 3),
                    # Niveau 3 — Semestre 6 (nouveaux)
                    ('GMX307', 'Intelligence artificielle pour la mécanique', 3, 2, 'MX', 6, 3),
                    ('GMX308', 'Energies renouvelables et systèmes mécaniques', 3, 2, 'MX', 6, 3),
                    ('GMX309', 'Robotique industrielle', 3, 2, 'TP', 6, 3),
                    ('GMX310', 'Matériaux composites et nouveaux matériaux', 3, 2, 'MX', 6, 3),
                    ('GMX311', 'Lean manufacturing et amélioration continue', 2, 1, 'MX', 6, 3),
                    ('GMX312', 'Projet de Fin d\'Études', 10, 6, 'MX', 6, 3),
                ]
            }
        }
        
        stats = {'specialites': 0, 'matieres': 0}
        
        for code, config in specialites_config.items():
            specialite = Specialite.objects.create(
                code=code,
                nom=config['nom'],
                description=config['description'],
                department=departments[code]
            )
            stats['specialites'] += 1
            self.stdout.write(f"✅ Spécialité: {code} - {config['nom']}")
            
            for matiere_tuple in config['matieres']:
                code_m, titre, credits, coef, nature, semestre, niveau = matiere_tuple
                
                Matiere.objects.create(
                    code=code_m,
                    titre=titre,
                    credits=credits,
                    coefficient=coef,
                    nature=nature,
                    specialite=specialite,
                    semestre=semestre,
                    niveau=niveau
                )
                stats['matieres'] += 1
                self.stdout.write(
                    f"  📚 {code_m} - {titre} "
                    f"(Semestre {semestre}, Niveau {niveau})"
                )
        
        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Seed terminé avec succès !"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"📊 {stats['specialites']} spécialités créées"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"📚 {stats['matieres']} matières créées avec niveaux"
        ))
        
        from django.db.models import Count
        niveau_stats = Matiere.objects.values('niveau').annotate(
            count=Count('id')
        ).order_by('niveau')
        
        self.stdout.write("\n📈 Distribution par niveau :")
        for stat in niveau_stats:
            self.stdout.write(f"  Niveau {stat['niveau']}: {stat['count']} matières")