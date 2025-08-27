# -*- coding: utf-8 -*-
# EcoSwitch Lite V3.2 — Base officielle
# Entrée principale : lance une simulation avec données locales

from client_data import load_client
from meteo_data import load_meteo
from simulateur import simulate_chauffage
from verdict_engine import recommander_solution
from eco_score import calculer_ecoscore
from rapport_client import generer_rapport

def main():
    client = load_client("demo_client.json")
    meteo = load_meteo("data/meteo_demo.csv")

    resultats = simulate_chauffage(client, meteo)
    verdict = recommander_solution(resultats, client)
    score = calculer_ecoscore(resultats)

    generer_rapport(client, resultats, verdict, score)

    print("✅ Simulation terminée")
    print("Verdict :", verdict)
    print("EcoScore global :", score)

if __name__ == "__main__":
    main()
