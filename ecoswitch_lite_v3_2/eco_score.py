# -*- coding: utf-8 -*-
def calculer_ecoscore(resultats: dict) -> int:
    a = resultats["aggregats"]
    cout_gaz = a["cout_gaz_eur"]
    cout_hybride = a["cout_hybride_eur"]
    co2_gaz = a["co2_gaz_kg"]
    co2_hybride = a["co2_hybride_kg"]

    # Gains relatifs (vs gaz seul)
    gain_euro = max(0.0, (cout_gaz - cout_hybride) / cout_gaz) if cout_gaz > 0 else 0.0
    gain_co2 = max(0.0, (co2_gaz - co2_hybride) / co2_gaz) if co2_gaz > 0 else 0.0

    score = 100.0 * (0.6 * gain_euro + 0.4 * gain_co2)
    score = int(round(max(0.0, min(100.0, score))))
    return score
