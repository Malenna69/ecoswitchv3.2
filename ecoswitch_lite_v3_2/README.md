# EcoSwitch Lite V3.2 — Base officielle

Version minimaliste, 100% locale (sans cloud), pour simuler un besoin de chauffage et comparer
PAC vs Chaudière Gaz vs Hybride (relevé) sur une météo horaire simplifiée.

## Installation
```bash
pip install -r requirements.txt
```

## Lancement
```bash
python main.py
```

## Fichiers clés
- `main.py` : point d’entrée
- `client_data.py` : charge `demo_client.json`
- `meteo_data.py` : charge `data/meteo_demo.csv`
- `simulateur.py` : simulateur énergétique + coûts/CO₂ (PAC, Gaz, Hybride)
- `verdict_engine.py` : verdict (PAC seule / PAC hybride / Chaudière)
- `eco_score.py` : EcoScore (économie + CO₂)
- `rapport_client.py` : génère `rapport_client.txt` + `resultats_horaires.csv`
- `data/tarifs_hp_hc.json`, `data/tarifs_tempo.json` : exemples de tarifs

## Hypothèses simplifiées (Lite)
- Modèle thermique statique : E = UA * (T_int - T_ext) par heure (>= 0)
- COP PAC dynamique ≈ f(T_ext, T_depart), borné [1.0, 5.5]
- Rendement chaudière constant (par défaut 0.92)
- Tarifs : base, HP/HC (23h–7h = HC), Tempo (démo = bleu)
- Facteurs CO₂ (France) : élec 0.06 kg/kWh, gaz 0.227 kg/kWh
- **Objectif :** pédagogie et cohérence — pas un calcul normatif complet (voir EcoSwitch Core v10.2).

© 2025 EcoSwitch — “Ne devinez plus — mesurez.”
