# -*- coding: utf-8 -*-
import pandas as pd

def generer_rapport(client: dict, resultats: dict, verdict: str, ecoscore: int):
    a = resultats["aggregats"]
    df = resultats["horaires"].copy()

    # Exports
    df.to_csv("resultats_horaires.csv", index=True, encoding="utf-8")

    with open("rapport_client.txt", "w", encoding="utf-8") as f:
        f.write("EcoSwitch Lite V3.2 — Rapport client\n")
        f.write("=====================================\n\n")
        f.write(f"Client : {client.get('nom','N/A')} — CP {client.get('code_postal','')}\n")
        f.write(f"UA : {client.get('ua_w_k')} W/K | T_confort : {client.get('t_confort')} °C\n")
        f.write(f"Rendement chaudière : {client.get('rendement_chaudiere')} | Mode tarif : {client.get('mode_tarif')}\n")
        f.write(f"T_depart PAC : {client.get('t_depart_pac')} °C\n\n")

        f.write("Synthèse énergétique & économique\n")
        f.write("---------------------------------\n")
        f.write(f"Énergie utile demandée : {a['energie_utile_kWh']:.1f} kWh\n")
        f.write(f"COP médian observé    : {a['cop_median']:.2f}\n\n")

        f.write("Scénarios comparés (totaux)\n")
        f.write("---------------------------\n")
        f.write(f"Gaz seul  : coût = {a['cout_gaz_eur']:.2f} €, CO₂ = {a['co2_gaz_kg']:.1f} kg\n")
        f.write(f"PAC seule : coût = {a['cout_pac_eur']:.2f} €, CO₂ = {a['co2_pac_kg']:.1f} kg\n")
        f.write(f"Hybride   : coût = {a['cout_hybride_eur']:.2f} €, CO₂ = {a['co2_hybride_kg']:.1f} kg\n")
        f.write(f"Part utile PAC en hybride : {a['part_utile_pac_hybride_%']:.1f} %\n\n")

        f.write("Recommandation\n")
        f.write("--------------\n")
        f.write(f"{verdict}\n\n")

        f.write("EcoScore (0–100)\n")
        f.write("----------------\n")
        f.write(f"{ecoscore}/100\n\n")

        f.write("Notes\n")
        f.write("-----\n")
        f.write("- Modèle Lite pédagogique. Pour une étude détaillée : EcoSwitch Core v10.2.\n")
        f.write("- Hypothèses CO₂ et tarifs simplifiées. Données 100% locales, sans cloud.\n")
        f.write("- « Ne devinez plus — mesurez. »\n")
