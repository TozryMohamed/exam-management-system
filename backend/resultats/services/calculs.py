def calcul_ue(resultats):
    total = 0
    coef_total = 0

    for r in resultats:
        coef = r.matiere.coefficient
        total += r.moyenne * coef
        coef_total += coef

    return total / coef_total if coef_total != 0 else 0


def calcul_semestre(ues):
    total = 0
    coef_total = 0

    for ue in ues:
        total += ue["moyenne"] * ue["coef"]
        coef_total += ue["coef"]

    return total / coef_total if coef_total != 0 else 0