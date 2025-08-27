# -*- coding: utf-8 -*-
def recommander_solution(resultats: dict, client: dict) -> str:
    a = resultats["aggregats"]

    cout_pac = a["cout_pac_eur"]
    cout_gaz = a["cout_gaz_eur"]
    cout_hybride = a["cout_hybride_eur"]
    cop_med = a["cop_median"] if a["cop_median"] == a["cop_median"] else 0.0  # NaN guard

    # Règles simples (Lite) — neutres et pédagogiques
    if (cout_pac <= 0.75 * cout_gaz) and (cop_med >= 2.5):
        return "🟢 PAC seule recommandée (économique et performante)"
    elif (cout_hybride <= 0.90 * cout_gaz):
        return "🔵 PAC hybride (en relève) recommandée"
    else:
        return "🟠 Conserver la chaudière (optimiser les réglages d’abord)"
