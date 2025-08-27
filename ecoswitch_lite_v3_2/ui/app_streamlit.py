# -*- coding: utf-8 -*-
# EcoSwitch Lite V3.2 — UI (Nest/Tesla/Starlink-inspired)
# Streamlit dashboard with brand styling and live simulation

import os, sys, pathlib
import pandas as pd
import plotly.express as px
import streamlit as st

# Make root modules importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from .brand import BRAND
from client_data import load_client
from meteo_data import load_meteo
from simulateur import simulate_chauffage
from verdict_engine import recommander_solution
from eco_score import calculer_ecoscore
from rapport_client import generer_rapport

st.set_page_config(page_title="EcoSwitch Lite V3.2", page_icon="🌿", layout="wide")

# ------------------ CSS styling ------------------
C = BRAND["colors"]
F = BRAND["fonts"]
st.markdown(f"""
<style>
:root {{
  --bg: {C["bg"]};
  --panel: {C["panel"]};
  --text: {C["text"]};
  --muted: {C["muted"]};
  --accent: {C["accent"]};
  --accentAlt: {C["accentAlt"]};
  --warn: {C["warn"]};
}}
/* Page */
.block-container {{
  padding: 2rem 2rem 3rem 2rem;
}}
body, .stApp {{
  background: radial-gradient(1200px 600px at 80% -10%, rgba(31,182,255,0.08), transparent 60%),
              radial-gradient(900px 500px at -10% 20%, rgba(22,193,114,0.10), transparent 55%),
              var(--bg);
  color: var(--text);
  font-family: {F["body"]};
}}
/* Panels */
.es-card {{
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 20px 22px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}}
/* Hero */
.es-hero h1 {{
  font-family: {F["heading"]};
  font-weight: 700;
  letter-spacing: -0.02em;
  font-size: 44px;
  margin: 0;
}}
.es-hero p {{
  color: var(--muted);
  margin: 6px 0 0 0;
  font-size: 16px;
}}
/* KPI */
.es-kpi {{
  display: flex; align-items: baseline; gap: 10px;
  font-weight: 700; font-size: 26px;
}}
.es-kpi span {{ color: var(--muted); font-weight: 500; font-size: 14px; }}
/* LED verdict */
.es-led {{
  width: 22px; height: 22px; border-radius: 999px;
  box-shadow: 0 0 12px currentColor, 0 0 24px currentColor;
  display: inline-block; vertical-align: middle;
}}
/* Buttons */
.es-cta {{
  display:inline-block; padding: 10px 16px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.10);
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
  color: var(--text); text-decoration: none; font-weight: 600;
}}
.es-cta:hover {{ border-color: rgba(255,255,255,0.25); }}
/* Tables/Plot tweaks */
thead th {{ color: var(--muted) !important; }}
</style>
""", unsafe_allow_html=True)

# ------------------ Sidebar controls ------------------
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    client = load_client(str(ROOT / "demo_client.json"))
    mode = st.selectbox("Mode tarif", ["base", "hp_hc", "tempo"], index=["base","hp_hc","tempo"].index(client.get("mode_tarif","base")))
    client["mode_tarif"] = mode

    if mode == "base":
        client["prix_elec_eur_kwh"] = st.number_input("Prix élec (€/kWh)", 0.01, 2.00, float(client["prix_elec_eur_kwh"]), 0.01)
    client["prix_gaz_eur_kwh"] = st.number_input("Prix gaz (€/kWh)", 0.01, 2.00, float(client["prix_gaz_eur_kwh"]), 0.01)

    st.divider()
    client["ua_w_k"] = st.slider("UA (W/K)", 80, 450, int(client["ua_w_k"]), 5)
    client["t_confort"] = st.slider("T° confort (°C)", 16.0, 22.0, float(client["t_confort"]), 0.5)
    client["t_depart_pac"] = st.slider("T° départ PAC (°C)", 35, 60, int(client["t_depart_pac"]), 1)

    run = st.button("🔁 Recalculer", use_container_width=True)

# ------------------ Load meteo & simulate ------------------
meteo = load_meteo(str(ROOT / "data" / "meteo_demo.csv"))
res = simulate_chauffage(client, meteo)
verdict = recommander_solution(res, client)
score = calculer_ecoscore(res)

# Generate report artifacts (for download)
generer_rapport(client, res, verdict, score)

a = res["aggregats"]
df = res["horaires"]

# ------------------ Hero ------------------
st.markdown(f"""
<div class="es-card es-hero">
  <h1>{BRAND["name"]} — Assistant Énergie</h1>
  <p>{BRAND["slogan"]}</p>
</div>
""", unsafe_allow_html=True)
st.write("")

# ------------------ KPI Row ------------------
col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])

# Verdict/LED
LED_COLOR = C["accent"] if verdict.startswith("🟢") else (C["accentAlt"] if verdict.startswith("🔵") else C["warn"])
with col1:
    st.markdown(f"""
    <div class="es-card">
      <div style="display:flex; align-items:center; gap:12px;">
        <div class="es-led" style="color:{LED_COLOR}; background:{LED_COLOR};"></div>
        <div>
          <div class="es-kpi">{verdict}</div>
          <div style="color:var(--muted); font-size:13px;">COP médian observé : {a["cop_median"]:.2f}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# EcoScore
with col2:
    st.markdown(f"""
    <div class="es-card">
      <div class="es-kpi">{score}<span>/100</span></div>
      <div style="color:var(--muted); font-size:13px;">EcoScore global</div>
    </div>
    """, unsafe_allow_html=True)

# Économies € vs gaz
economie_eur = max(0.0, a["cout_gaz_eur"] - a["cout_hybride_eur"])
with col3:
    st.markdown(f"""
    <div class="es-card">
      <div class="es-kpi">{economie_eur:,.2f}<span>€ vs gaz</span></div>
      <div style="color:var(--muted); font-size:13px;">Période simulée</div>
    </div>
    """, unsafe_allow_html=True)

# CO2 évités
co2_evites = max(0.0, a["co2_gaz_kg"] - a["co2_hybride_kg"])
with col4:
    st.markdown(f"""
    <div class="es-card">
      <div class="es-kpi">{co2_evites:,.1f}<span>kg CO₂ évités</span></div>
      <div style="color:var(--muted); font-size:13px;">Période simulée</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ------------------ Plot: Coûts cumulés ------------------
plot_df = df.reset_index()[["datetime","Cout_pac_eur","Cout_gaz_eur"]].rename(columns={
    "datetime":"Date/Heure", "Cout_pac_eur":"PAC (€)", "Cout_gaz_eur":"Gaz (€)"
})
fig = px.line(plot_df, x="Date/Heure", y=["PAC (€)", "Gaz (€)"], title="Coûts cumulés — PAC vs Gaz (période simulée)")
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color=C["text"], title_font_size=18, legend_title_text=""
)
st.plotly_chart(fig, use_container_width=True)

# ------------------ Downloads (in-memory) ------------------
import io
# Build report text in memory (consistent with rapport_client.py)
a = res["aggregats"]
report = io.StringIO()
report.write("EcoSwitch Lite V3.2 — Rapport client\n")
report.write("=====================================\n\n")
report.write(f"Client : {client.get('nom','N/A')} — CP {client.get('code_postal','')}\n")
report.write(f"UA : {client.get('ua_w_k')} W/K | T_confort : {client.get('t_confort')} °C\n")
report.write(f"Rendement chaudière : {client.get('rendement_chaudiere')} | Mode tarif : {client.get('mode_tarif')}\n")
report.write(f"T_depart PAC : {client.get('t_depart_pac')} °C\n\n")
report.write("Synthèse énergétique & économique\n")
report.write("---------------------------------\n")
report.write(f"Énergie utile demandée : {a['energie_utile_kWh']:.1f} kWh\n")
report.write(f"COP médian observé    : {a['cop_median']:.2f}\n\n")
report.write("Scénarios comparés (totaux)\n")
report.write("---------------------------\n")
report.write(f"Gaz seul  : coût = {a['cout_gaz_eur']:.2f} €, CO₂ = {a['co2_gaz_kg']:.1f} kg\n")
report.write(f"PAC seule : coût = {a['cout_pac_eur']:.2f} €, CO₂ = {a['co2_pac_kg']:.1f} kg\n")
report.write(f"Hybride   : coût = {a['cout_hybride_eur']:.2f} €, CO₂ = {a['co2_hybride_kg']:.1f} kg\n")
report.write(f"Part utile PAC en hybride : {a['part_utile_pac_hybride_%']:.1f} %\n\n")
report.write("Recommandation\n")
report.write("--------------\n")
report.write(f"{verdict}\n\n")
report.write("EcoScore (0–100)\n")
report.write("----------------\n")
report.write(f"{score}/100\n\n")
report.write("Notes\n")
report.write("-----\n")
report.write("- Modèle Lite pédagogique. Pour une étude détaillée : EcoSwitch Core v10.2.\n")
report.write("- Hypothèses CO₂ et tarifs simplifiées. Données 100% locales, sans cloud.\n")
report.write("- « Ne devinez plus — mesurez. »\n")
report_bytes = report.getvalue().encode("utf-8")

# CSV export in memory
csv_buf = io.StringIO()
df.reset_index().to_csv(csv_buf, index=False)
csv_bytes = csv_buf.getvalue().encode("utf-8")

st.download_button("📄 Télécharger le rapport client", data=report_bytes, file_name="rapport_client.txt", mime="text/plain", key="dl_rapport_mem")
st.download_button("🧾 Télécharger les résultats horaires (CSV)", data=csv_bytes, file_name="resultats_horaires.csv", mime="text/csv", key="dl_csv_mem")

st.markdown('<a class="es-cta" href="#" onclick="window.location.reload();return false;">🔄 Actualiser l\\'affichage</a>', unsafe_allow_html=True)
