
# groups/urls.py
from django.urls import path
from .views import (
    GroupeListCreateView,
    GroupeDetailView,
    RepartitionListCreateView,
    RepartitionDetailView,
    RepartitionDetailListView,
    melange_intelligent,
    appliquer_melange,
    melange_avec_etudiants_reels,
    get_repartition_suggestions,
    verifier_capacite,
    mes_places,
    get_historique_regroupements,
    get_historique_details,
    telecharger_pdf_historique,
)

urlpatterns = [
    # CRUD Groupes
    path("groupes/", GroupeListCreateView.as_view(), name="groupes-list"),
    path("groupes/<int:pk>/", GroupeDetailView.as_view(), name="groupe-detail"),
    
    # CRUD Répartitions
    path("repartitions/", RepartitionListCreateView.as_view(), name="repartitions-list"),
    path("repartitions/<int:pk>/", RepartitionDetailView.as_view(), name="repartition-detail"),
    path("repartitions-details/", RepartitionDetailListView.as_view(), name="repartitions-details-list"),
    
    # Actions
    path("melange-intelligent/", melange_intelligent, name="melange-intelligent"),
    path("appliquer-melange/", appliquer_melange, name="appliquer-melange"),
    path("melange-etudiants-reels/", melange_avec_etudiants_reels, name="melange-etudiants-reels"),
    path("suggestions/<int:examen_id>/", get_repartition_suggestions, name="repartition-suggestions"),
    path("verifier-capacite/", verifier_capacite, name="verifier-capacite"),
    path("mes-places/", mes_places, name="mes-places"),

    path("historique-regroupements/", get_historique_regroupements, name="historique-regroupements"),
    path("historique-regroupements/<str:session_key>/", get_historique_details, name="historique-details"),
    path("telecharger-pdf/<str:session_key>/", telecharger_pdf_historique, name="telecharger-pdf"),
]