# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import json

# Facteurs CO2 (France, ordre de grandeur)
CO2_ELEC = 0.06   # kg/kWh
CO2_GAZ  = 0.227  # kg/kWh

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def cop_pac(t_ext, t_depart=50):
    """
    COP dynamique (approx.) : basé sur des courbes génériques EN 14825.
    - Sensible à la T° extérieure et à la T° de départ d'eau.
    - Borné [1.0, 5.5] pour rester réaliste.
    """
    # Référence : COP ≈ 3.2 @ 7°C ext, départ 35°C
    base = 3.2 + 0.07 * (t_ext - 7) - 0.015 * (t_depart - 35)
    return clamp(base, 1.0, 5.5)

def _tarif_base(client):
    return client["prix_elec_eur_kwh"], client["prix_gaz_eur_kwh"]

def _tarif_hp_hc(hour, json_path="data/tarifs_hp_hc.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        t = json.load(f)
    if hour in t["heures_creuses"]:
        return t["hc_eur_kwh"]
    return t["hp_eur_kwh"]

def _tarif_tempo(hour, couleur=None, json_path="data/tarifs_tempo.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        t = json.load(f)
    if couleur is None:
        couleur = t.get("default_couleur", "bleu")
    hp_hc = t[couleur]
    if hour in t["heures_creuses"]:
        return hp_hc["hc"]
    return hp_hc["hp"]

def simulate_chauffage(client: dict, meteo: pd.DataFrame) -> dict:
    """
    Calcule la demande énergétique horaire et compare 3 scénarios :
    - Gaz seul
    - PAC seule
    - Hybride (choix horaire du coût utile le plus bas)
    Retourne un dict avec agrégats + séries horaires.
    """
    ua = float(client["ua_w_k"])
    t_int = float(client["t_confort"])
    eta_gaz = float(client["rendement_chaudiere"])
    t_depart = float(client.get("t_depart_pac", 50))
    mode_tarif = client.get("mode_tarif", "base")

    # Prépare DataFrame
    df = meteo.copy().rename(columns={"t_ext": "T_ext"})
    df["dT"] = (t_int - df["T_ext"]).clip(lower=0.0)
    # Besoin utile (kWh) par heure
    df["E_utile_kWh"] = (ua * df["dT"] / 1000.0).round(4)

    # COP & rendements
    df["COP"] = df["T_ext"].apply(lambda T: cop_pac(T, t_depart=t_depart))

    # Tarifs élec/ gaz
    if mode_tarif == "base":
        prix_elec, prix_gaz = _tarif_base(client)
        df["prix_elec"] = prix_elec
        df["prix_gaz"] = prix_gaz
    elif mode_tarif == "hp_hc":
        df["prix_elec"] = [ _tarif_hp_hc(ts.hour) for ts in df.index ]
        # gaz constant via client
        _, prix_gaz = _tarif_base(client)
        df["prix_gaz"] = prix_gaz
    elif mode_tarif == "tempo":
        # démo: toute la période en "bleu"
        df["prix_elec"] = [ _tarif_tempo(ts.hour, couleur="bleu") for ts in df.index ]
        _, prix_gaz = _tarif_base(client)
        df["prix_gaz"] = prix_gaz
    else:
        # fallback
        prix_elec, prix_gaz = _tarif_base(client)
        df["prix_elec"] = prix_elec
        df["prix_gaz"] = prix_gaz

    # Scénario Gaz seul
    df["E_gaz_kWh_in"] = (df["E_utile_kWh"] / eta_gaz).fillna(0.0)
    df["Cout_gaz_eur"] = df["E_gaz_kWh_in"] * df["prix_gaz"]
    df["CO2_gaz_kg"] = df["E_gaz_kWh_in"] * CO2_GAZ

    # Scénario PAC seule
    df["E_elec_pac_kWh_in"] = (df["E_utile_kWh"] / df["COP"]).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    df["Cout_pac_eur"] = df["E_elec_pac_kWh_in"] * df["prix_elec"]
    df["CO2_pac_kg"] = df["E_elec_pac_kWh_in"] * CO2_ELEC

    # Coût utile instantané (€/kWh_utile)
    df["cout_utile_pac"] = df["prix_elec"] / df["COP"]
    df["cout_utile_gaz"] = df["prix_gaz"] / eta_gaz

    # Scénario Hybride : choisir le moins cher à l'heure
    use_pac = df["cout_utile_pac"] <= df["cout_utile_gaz"]
    df["E_utile_pac_kWh"] = np.where(use_pac, df["E_utile_kWh"], 0.0)
    df["E_utile_gaz_kWh"] = np.where(~use_pac, df["E_utile_kWh"], 0.0)

    df["E_elec_hybride_kWh_in"] = (df["E_utile_pac_kWh"] / df["COP"]).fillna(0.0)
    df["E_gaz_hybride_kWh_in"] = (df["E_utile_gaz_kWh"] / eta_gaz).fillna(0.0)

    df["Cout_hybride_eur"] = df["E_elec_hybride_kWh_in"] * df["prix_elec"] + df["E_gaz_hybride_kWh_in"] * df["prix_gaz"]
    df["CO2_hybride_kg"] = df["E_elec_hybride_kWh_in"] * CO2_ELEC + df["E_gaz_hybride_kWh_in"] * CO2_GAZ

    # Agrégats
    aggregats = {
        "energie_utile_kWh": df["E_utile_kWh"].sum(),
        "cop_median": df.loc[df["E_utile_kWh"] > 0, "COP"].median() if (df["E_utile_kWh"] > 0).any() else float("nan"),

        "energie_in_pac_kWh": df["E_elec_pac_kWh_in"].sum(),
        "cout_pac_eur": df["Cout_pac_eur"].sum(),
        "co2_pac_kg": df["CO2_pac_kg"].sum(),

        "energie_in_gaz_kWh": df["E_gaz_kWh_in"].sum(),
        "cout_gaz_eur": df["Cout_gaz_eur"].sum(),
        "co2_gaz_kg": df["CO2_gaz_kg"].sum(),

        "energie_in_hybride_elec_kWh": df["E_elec_hybride_kWh_in"].sum(),
        "energie_in_hybride_gaz_kWh": df["E_gaz_hybride_kWh_in"].sum(),
        "cout_hybride_eur": df["Cout_hybride_eur"].sum(),
        "co2_hybride_kg": df["CO2_hybride_kg"].sum(),
    }
    # Part d'énergie utile couverte par PAC en mode Hybride
    utile_tot = df["E_utile_kWh"].sum()
    useful_pac = df["E_utile_pac_kWh"].sum()
    aggregats["part_utile_pac_hybride_%"] = (100.0 * useful_pac / utile_tot) if utile_tot > 0 else 0.0

    return {
        "aggregats": aggregats,
        "horaires": df  # pour export
    }
