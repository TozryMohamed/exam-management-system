# from django.db import models
# from django.conf import settings
# from matieres.models import Matiere
# import logging

# logger = logging.getLogger(__name__)


# class ResultatMatiere(models.Model):
#     """
#     Modèle pour stocker les résultats d'un étudiant dans une matière.
#     Architecture temporaire avec session principale/rattrapage.
    
#     RÈGLES DE CALCUL :
#     ================
#     MX sans TP : oral*0.1 + ds*0.2 + exam*0.7
#     MX avec TP  : oral*0.1 + ds*0.1 + tp*0.1 + exam*0.7
#     CC          : oral*0.2 + exam*0.8
#     TP          : tp (uniquement la note de TP)
    
#     Rattrapage : max(moyenne_principale, moyenne_avec_exam_r)
#     """
    
#     SESSION_CHOICES = (
#         ('principale', 'Session Principale'),
#         ('rattrapage', 'Session Rattrapage'),
#     )

#     etudiant = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='resultats'
#     )

#     matiere = models.ForeignKey(
#         Matiere,
#         on_delete=models.CASCADE,
#         related_name='resultats'
#     )

#     session = models.CharField(
#         max_length=20,
#         choices=SESSION_CHOICES,
#         default='principale'
#     )

#     # Notes brutes
#     oral = models.FloatField(default=0)
#     ds = models.FloatField(default=0)
#     exam = models.FloatField(default=0)
#     tp = models.FloatField(default=0)
#     exam_r = models.FloatField(default=0)

#     # Moyenne calculée
#     moyenne = models.FloatField(default=0)
    
#     # Validation
#     is_validated = models.BooleanField(default=False)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('etudiant', 'matiere', 'session')
#         ordering = ['matiere__semestre', 'matiere__code']
#         verbose_name = "Résultat Matière"
#         verbose_name_plural = "Résultats Matières"

#     def __str__(self):
#         return f"{self.etudiant.username} - {self.matiere.code} ({self.get_session_display()})"

#     # ==========================================
#     # 🔧 MÉTHODES DE CALCUL STATIQUES
#     # ==========================================

#     @staticmethod
#     def calculer_session_principale(matiere, oral, ds, exam, tp):
#         """
#         Calcule la moyenne de la session principale selon la nature de la matière.
        
#         Règles :
#         - MX sans TP : oral*0.1 + ds*0.2 + exam*0.7
#         - MX avec TP  : oral*0.1 + ds*0.1 + tp*0.1 + exam*0.7
#         - CC          : oral*0.2 + exam*0.8
#         - TP pur      : tp (si uniquement TP présent)
#         - TP mixte    : oral*0.1 + ds*0.1 + tp*0.1 + exam*0.7 (si autres notes présentes)
        
#         Returns:
#             float: Moyenne calculée, ou 0 si aucune note saisie
#         """
#         # Vérifier si des notes sont saisies
#         has_notes = any([oral > 0, ds > 0, exam > 0, tp > 0])
#         if not has_notes:
#             return 0.0

#         nature = matiere.nature if matiere else "MX"
        
#         if nature == "MX":
#             # Matière Mixte
#             has_tp = tp > 0
#             has_autres_notes = any([oral > 0, ds > 0, exam > 0])
            
#             if has_tp and not has_autres_notes:
#                 # TP uniquement (cas rare mais possible)
#                 moyenne = tp
#             elif has_tp and has_autres_notes:
#                 # MX avec TP : oral*0.1 + ds*0.1 + tp*0.1 + exam*0.7
#                 moyenne = oral * 0.1 + ds * 0.1 + tp * 0.1 + exam * 0.7
#             else:
#                 # MX sans TP : oral*0.1 + ds*0.2 + exam*0.7
#                 moyenne = oral * 0.1 + ds * 0.2 + exam * 0.7
                
#         elif nature == "TP":
#             # Matière TP pure
#             has_autres_notes = any([oral > 0, ds > 0, exam > 0])
            
#             if has_autres_notes:
#                 # TP avec autres notes : formule MX avec TP
#                 moyenne = oral * 0.1 + ds * 0.1 + tp * 0.1 + exam * 0.7
#             else:
#                 # TP pure : uniquement la note de TP
#                 moyenne = tp
                
#         elif nature == "CC":
#             # Contrôle Continu : oral*0.2 + exam*0.8
#             moyenne = oral * 0.2 + exam * 0.8
            
#         else:
#             # Fallback : moyenne simple des notes présentes
#             notes = [n for n in [oral, ds, exam, tp] if n > 0]
#             moyenne = sum(notes) / len(notes) if notes else 0.0
            
#         return round(moyenne, 2)

#     @staticmethod
#     def calculer_session_rattrapage(matiere, moyenne_principale, oral_principale, ds_principale, tp_principale, exam_r):
#         """
#         Calcule la moyenne de rattrapage et retourne la meilleure des deux.
        
#         Formule : moyenne_finale = max(moyenne_principale, moyenne_rattrapage)
        
#         Args:
#             matiere: L'objet Matiere
#             moyenne_principale: Moyenne déjà calculée de la session principale
#             oral_principale: Note d'oral de la session principale
#             ds_principale: Note de DS de la session principale
#             tp_principale: Note de TP de la session principale
#             exam_r: Note d'examen de rattrapage
            
#         Returns:
#             float: Meilleure moyenne entre session principale et rattrapage
#         """
#         if exam_r <= 0:
#             return moyenne_principale
            
#         nature = matiere.nature if matiere else "MX"
        
#         if nature == "MX":
#             # Matière Mixte
#             has_tp = tp_principale > 0
#             has_autres_notes = any([oral_principale > 0, ds_principale > 0])
            
#             if has_tp and not has_autres_notes:
#                 # TP uniquement, le rattrapage ne change rien
#                 moyenne_rattrapage = tp_principale
#             elif has_tp and has_autres_notes:
#                 # MX avec TP : on remplace exam par exam_r
#                 moyenne_rattrapage = oral_principale * 0.1 + ds_principale * 0.1 + tp_principale * 0.1 + exam_r * 0.7
#             else:
#                 # MX sans TP : on remplace exam par exam_r
#                 moyenne_rattrapage = oral_principale * 0.1 + ds_principale * 0.2 + exam_r * 0.7
                
#         elif nature == "TP":
#             # Matière TP
#             has_autres_notes = any([oral_principale > 0, ds_principale > 0])
            
#             if has_autres_notes:
#                 # TP avec autres notes : on remplace exam par exam_r
#                 moyenne_rattrapage = oral_principale * 0.1 + ds_principale * 0.1 + tp_principale * 0.1 + exam_r * 0.7
#             else:
#                 # TP pure : le rattrapage ne change rien (pas d'exam)
#                 moyenne_rattrapage = tp_principale
                
#         elif nature == "CC":
#             # Contrôle Continu : on remplace exam par exam_r
#             moyenne_rattrapage = oral_principale * 0.2 + exam_r * 0.8
            
#         else:
#             # Fallback : l'examen de rattrapage remplace tout
#             moyenne_rattrapage = exam_r
            
#         moyenne_rattrapage = round(moyenne_rattrapage, 2)
        
#         # Retourner la meilleure des deux moyennes
#         return round(max(moyenne_principale, moyenne_rattrapage), 2)

#     # ==========================================
#     # 💾 MÉTHODE SAVE REFACTORISÉE
#     # ==========================================

#     def save(self, *args, **kwargs):
#         """
#         Sauvegarde avec calcul automatique de la moyenne.
#         AUCUN appel récursif à save() !
#         Utilise update() pour éviter la récursion infinie.
#         """
#         if self.session == 'principale':
#             # Calcul session principale
#             self.moyenne = self.calculer_session_principale(
#                 matiere=self.matiere,
#                 oral=self.oral,
#                 ds=self.ds,
#                 exam=self.exam,
#                 tp=self.tp
#             )
#             # Pas de rattrapage pour la session principale
#             self.exam_r = 0
            
#         elif self.session == 'rattrapage':
#             # Récupérer la session principale existante
#             try:
#                 resultat_principal = ResultatMatiere.objects.get(
#                     etudiant=self.etudiant,
#                     matiere=self.matiere,
#                     session='principale'
#                 )
                
#                 # Calculer la moyenne avec rattrapage
#                 self.moyenne = self.calculer_session_rattrapage(
#                     matiere=self.matiere,
#                     moyenne_principale=resultat_principal.moyenne,
#                     oral_principale=resultat_principal.oral,
#                     ds_principale=resultat_principal.ds,
#                     tp_principale=resultat_principal.tp,
#                     exam_r=self.exam_r
#                 )
                
#                 # Mettre à jour la session principale si rattrapage meilleur
#                 if self.moyenne > resultat_principal.moyenne:
#                     # ✅ Mise à jour directe en base SANS appel à save()
#                     ResultatMatiere.objects.filter(
#                         id=resultat_principal.id
#                     ).update(
#                         moyenne=self.moyenne,
#                         is_validated=self.moyenne >= 10,
#                         exam_r=self.exam_r  # Garder trace de la note de rattrapage
#                     )
#                     logger.info(
#                         f"✅ Rattrapage réussi pour {self.etudiant.username} "
#                         f"en {self.matiere.code}: {resultat_principal.moyenne} → {self.moyenne}"
#                     )
                    
#             except ResultatMatiere.DoesNotExist:
#                 # Pas de session principale, calcul simple avec exam_r
#                 logger.warning(
#                     f"⚠️ Pas de session principale trouvée pour {self.etudiant.username} "
#                     f"en {self.matiere.code}, calcul avec exam_r uniquement"
#                 )
#                 self.moyenne = round(self.exam_r, 2) if self.exam_r > 0 else 0

#         # Validation (moyenne >= 10)
#         self.is_validated = self.moyenne >= 10

#         # Sauvegarde finale (UN SEUL appel à super().save())
#         super().save(*args, **kwargs)

#     # ==========================================
#     # 📊 MÉTHODES DE CALCUL HIÉRARCHIQUE
#     # ==========================================

#     @staticmethod
#     def calculer_moyenne_semestre(etudiant, semestre):
#         """
#         Calcule la moyenne d'un semestre pour un étudiant.
#         Ne prend en compte QUE les matières avec des notes saisies (moyenne > 0).
        
#         Args:
#             etudiant: L'utilisateur étudiant
#             semestre: Numéro du semestre (1 à 6)
        
#         Returns:
#             float: Moyenne du semestre pondérée par les coefficients
#         """
#         resultats = ResultatMatiere.objects.filter(
#             etudiant=etudiant,
#             matiere__semestre=semestre,
#             session='principale',
#             moyenne__gt=0  # Exclure les matières sans notes
#         ).select_related('matiere')
        
#         if not resultats.exists():
#             return 0.0
        
#         # Moyenne pondérée par les coefficients
#         total_pondere = 0
#         total_coefficients = 0
        
#         for resultat in resultats:
#             coeff = resultat.matiere.coefficient or 1
#             total_pondere += resultat.moyenne * coeff
#             total_coefficients += coeff
        
#         return round(total_pondere / total_coefficients, 2) if total_coefficients > 0 else 0.0

#     @staticmethod
#     def calculer_moyenne_annuelle(etudiant, annee):
#         """
#         Calcule la moyenne annuelle : (S1 + S2) / 2 pour l'année 1, etc.
        
#         Args:
#             etudiant: L'utilisateur étudiant
#             annee: 1 pour S1+S2, 2 pour S3+S4, 3 pour S5+S6
        
#         Returns:
#             float: Moyenne annuelle
#         """
#         semestre1 = (annee - 1) * 2 + 1
#         semestre2 = semestre1 + 1
        
#         moyenne_s1 = ResultatMatiere.calculer_moyenne_semestre(etudiant, semestre1)
#         moyenne_s2 = ResultatMatiere.calculer_moyenne_semestre(etudiant, semestre2)
        
#         # Si un semestre n'a pas de notes, on ne le compte pas
#         semestres_valides = []
#         if moyenne_s1 > 0:
#             semestres_valides.append(moyenne_s1)
#         if moyenne_s2 > 0:
#             semestres_valides.append(moyenne_s2)
        
#         if not semestres_valides:
#             return 0.0
        
#         return round(sum(semestres_valides) / len(semestres_valides), 2)

#     @staticmethod
#     def calculer_moyenne_generale(etudiant):
#         """
#         Calcule la moyenne générale selon la hiérarchie correcte :
#         Année 1 (S1+S2) + Année 2 (S3+S4) + Année 3 (S5+S6) / 3
        
#         Args:
#             etudiant: L'utilisateur étudiant
            
#         Returns:
#             float: Moyenne générale
#         """
#         moyennes_annuelles = []
        
#         for annee in [1, 2, 3]:
#             moyenne_annuelle = ResultatMatiere.calculer_moyenne_annuelle(etudiant, annee)
#             if moyenne_annuelle > 0:
#                 moyennes_annuelles.append(moyenne_annuelle)
        
#         if not moyennes_annuelles:
#             return 0.0
        
#         return round(sum(moyennes_annuelles) / len(moyennes_annuelles), 2)

#     # ==========================================
#     # 📋 MÉTHODES UTILITAIRES
#     # ==========================================

#     @property
#     def nature_matiere(self):
#         """Retourne la nature de la matière associée"""
#         return self.matiere.nature if self.matiere else "MX"

#     @property
#     def has_tp(self):
#         """Vérifie si la matière a une note de TP"""
#         return self.tp > 0

#     @property
#     def has_rattrapage(self):
#         """Vérifie si une note de rattrapage est saisie"""
#         return self.exam_r > 0

#     @property
#     def mention(self):
#         """Retourne la mention correspondant à la moyenne"""
#         if self.moyenne >= 16:
#             return "Très Bien"
#         elif self.moyenne >= 14:
#             return "Bien"
#         elif self.moyenne >= 12:
#             return "Assez Bien"
#         elif self.moyenne >= 10:
#             return "Passable"
#         else:
#             return "Insuffisant"

#     @classmethod
#     def get_resultats_etudiant(cls, etudiant, with_rattrapage=True):
#         """
#         Récupère tous les résultats d'un étudiant avec la meilleure moyenne
#         (principale ou rattrapage).
        
#         Args:
#             etudiant: L'utilisateur étudiant
#             with_rattrapage: Si True, prend en compte le rattrapage
            
#         Returns:
#             QuerySet: Résultats filtrés
#         """
#         resultats = cls.objects.filter(
#             etudiant=etudiant,
#             session='principale'
#         ).select_related('matiere')
        
#         return resultats

#     @classmethod
#     def get_statistiques_etudiant(cls, etudiant):
#         """
#         Retourne toutes les statistiques d'un étudiant en un seul appel.
        
#         Returns:
#             dict: Statistiques complètes
#         """
#         resultats = cls.get_resultats_etudiant(etudiant)
        
#         stats = {
#             'total_matieres': resultats.count(),
#             'matieres_validees': resultats.filter(is_validated=True).count(),
#             'matieres_non_validees': resultats.filter(is_validated=False, moyenne__gt=0).count(),
#             'matieres_sans_notes': resultats.filter(moyenne=0).count(),
#             'moyenne_generale': cls.calculer_moyenne_generale(etudiant),
#             'moyennes_semestres': {},
#             'moyennes_annuelles': {},
#         }
        
#         # Moyennes par semestre
#         for semestre in range(1, 7):
#             stats['moyennes_semestres'][f'S{semestre}'] = cls.calculer_moyenne_semestre(etudiant, semestre)
        
#         # Moyennes annuelles
#         for annee in range(1, 4):
#             stats['moyennes_annuelles'][f'Année {annee}'] = cls.calculer_moyenne_annuelle(etudiant, annee)
        
#         return stats







# resultats/models.py
from django.db import models
from django.conf import settings
from matieres.models import Matiere
import logging

logger = logging.getLogger(__name__)


class ResultatMatiere(models.Model):
    SESSION_CHOICES = (
        ('principale', 'Session Principale'),
        ('rattrapage', 'Session Rattrapage'),
    )

    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resultats'
    )

    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name='resultats'
    )

    session = models.CharField(
        max_length=20,
        choices=SESSION_CHOICES,
        default='principale'
    )

    oral = models.FloatField(default=0)
    ds = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    tp = models.FloatField(default=0)
    exam_r = models.FloatField(default=0)

    moyenne = models.FloatField(default=0)
    moyenne_finale = models.FloatField(default=0)
    is_validated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('etudiant', 'matiere', 'session')
        ordering = ['matiere__semestre', 'matiere__code']

    def __str__(self):
        return f"{self.etudiant.username} - {self.matiere.code}"

    @staticmethod
    def calculer_moyenne_principale(matiere, oral, ds, exam, tp):
        has_notes = any([oral > 0, ds > 0, exam > 0, tp > 0])
        if not has_notes:
            return 0.0

        nature = matiere.nature if matiere else "MX"
        
        if nature == "MX":
            has_tp = tp > 0
            has_autres = any([oral > 0, ds > 0, exam > 0])
            if has_tp and not has_autres:
                return tp
            elif has_tp and has_autres:
                return oral * 0.1 + ds * 0.1 + tp * 0.1 + exam * 0.7
            else:
                return oral * 0.1 + ds * 0.2 + exam * 0.7
        elif nature == "TP":
            has_autres = any([oral > 0, ds > 0, exam > 0])
            if has_autres:
                return oral * 0.1 + ds * 0.1 + tp * 0.1 + exam * 0.7
            return tp
        elif nature == "CC":
            return oral * 0.2 + exam * 0.8
        else:
            notes = [n for n in [oral, ds, exam, tp] if n > 0]
            return sum(notes) / len(notes) if notes else 0.0

    @staticmethod
    def calculer_moyenne_rattrapage(matiere, moyenne_principale, oral_p, ds_p, tp_p, exam_r):
        if exam_r <= 0:
            return moyenne_principale
        nature = matiere.nature if matiere else "MX"
        if nature == "MX":
            has_tp = tp_p > 0
            has_autres = any([oral_p > 0, ds_p > 0])
            if has_tp and not has_autres:
                return tp_p
            elif has_tp and has_autres:
                return oral_p * 0.1 + ds_p * 0.1 + tp_p * 0.1 + exam_r * 0.7
            else:
                return oral_p * 0.1 + ds_p * 0.2 + exam_r * 0.7
        elif nature == "TP":
            has_autres = any([oral_p > 0, ds_p > 0])
            if has_autres:
                return oral_p * 0.1 + ds_p * 0.1 + tp_p * 0.1 + exam_r * 0.7
            return tp_p
        elif nature == "CC":
            return oral_p * 0.2 + exam_r * 0.8
        else:
            return exam_r

    def save(self, *args, **kwargs):
        if self.session == 'principale':
            self.moyenne = round(self.calculer_moyenne_principale(
                self.matiere, self.oral, self.ds, self.exam, self.tp
            ), 2)
            self.exam_r = 0
            self.moyenne_finale = self.moyenne
            self.is_validated = self.moyenne >= 10
        elif self.session == 'rattrapage':
            try:
                principal = ResultatMatiere.objects.get(
                    etudiant=self.etudiant, matiere=self.matiere, session='principale'
                )
                self.moyenne = round(self.calculer_moyenne_rattrapage(
                    self.matiere, principal.moyenne, principal.oral, principal.ds, principal.tp, self.exam_r
                ), 2)
                self.moyenne_finale = max(principal.moyenne, self.moyenne)
                self.is_validated = self.moyenne_finale >= 10
            except ResultatMatiere.DoesNotExist:
                self.moyenne = round(self.exam_r, 2) if self.exam_r > 0 else 0
                self.moyenne_finale = self.moyenne
                self.is_validated = self.moyenne >= 10
        super().save(*args, **kwargs)