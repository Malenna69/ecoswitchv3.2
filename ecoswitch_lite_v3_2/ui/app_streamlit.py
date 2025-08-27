# -*- coding: utf-8 -*-
# EcoSwitch Lite V3.2 — UI (Nest/Tesla/Starlink-inspired) — Safe for Python 3.13

import os, sys, pathlib, io
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

st.set_page_config(page_title="EcoSwitch Lite V3.2", page_icon="🌿", layout="wide")

C = BRAND["colors"]
F = BRAND["fonts"]

# Inject CSS using string.Template to avoid f-string brace issues
from string import Template as _Tpl
_css = _Tpl("""<style>
:root {
  --bg: $bg;
  --panel: $panel;
  --text: $text;
  --muted: $muted;
  --accent: $accent;
  --accentAlt: $accentAlt;
  --warn: $warn;
}
/* Page */
.block-container {
  padding: 2rem 2rem 3rem 2rem;
}
body, .stApp {
  background: radial-gradient(1200px 600px at 80% -10%, rgba(31,182,255,0.08), transparent 60%),
              radial-gradient(900px 500px at -10% 20%, rgba(22,193,114,0.10), transparent 55%),
              var(--bg);
  color: var(--text);
  font-family: $font_body;
}
/* Panels */
.es-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 20px 22px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
/* Hero */
.es-hero h1 {
  font-family: $font_heading;
  font-weight: 700;
  letter-spacing: -0.02em;
  font-size: 44px;
  margin: 0;
}
.es-hero p {
  color: var(--muted);
  margin: 6px 0 0 0;
  font-size: 16px;
}
/* KPI */
.es-kpi {
  display: flex; align-items: baseline; gap: 10px;
  font-weight: 700; font-size: 26px;
}
.es-kpi span { color: var(--muted); font-weight: 500; font-size: 14px; }
/* LED verdict */
.es-led {
  width: 22px; height: 22px; border-radius: 999px;
  box-shadow: 0 0 12px currentColor, 0 0 24px currentColor;
  display: inline-block; vertical-align: middle;
}
/* Buttons */
.es-cta {
  display:inline-block; padding: 10px 16px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.10);
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
  color: var(--text); text-decoration: none; font-weight: 600;
}
.es-cta:hover { border-color: rgba(255,255,255,0.25); }
/* Tables/Plot tweaks */
thead th { color: var(--muted) !important; }
</style>
""").substitute(
    bg=C["bg"], panel=C["panel"], text=C["text"], muted=C["muted"],
    accent=C["accent"], accentAlt=C["accentAlt"], warn=C["warn"],
    font_body=F["body"], font_heading=F["heading"]
)
st.markdown(_css, unsafe_allow_html=True)

# ------------------ Sidebar controls ------------------
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    client = load_client(str(ROOT / "demo_client.json"))
    mode_list = ["base", "hp_hc", "tempo"]
    mode_idx = mode_list.index(client.get("mode_tarif", "base")) if client.get("mode_tarif", "base") in mode_list else 0
    mode = st.selectbox("Mode tarif", mode_list, index=mode_idx)
    client["mode_tarif"] = mode

    if mode == "base":
        client["prix_elec_eur_kwh"] = st.number_input("Prix élec (€/kWh)", min_value=0.01, max_value=2.00, value=float(client["prix_elec_eur_kwh"]), step=0.01)
    client["prix_gaz_eur_kwh"] = st.number_input("Prix gaz (€/kWh)", min_value=0.01, max_value=2.00, value=float(client["prix_gaz_eur_kwh"]), step=0.01)

    st.divider()
    client["ua_w_k"] = int(st.slider("UA (W/K)", min_value=80, max_value=450, value=int(client["ua_w_k"]), step=5))
    client["t_confort"] = float(st.slider("T° confort (°C)", min_value=16.0, max_value=22.0, value=float(client["t_confort"]), step=0.5))
    client["t_depart_pac"] = int(st.slider("T° départ PAC (°C)", min_value=35, max_value=60, value=int(client["t_depart_pac"]), step=1))

# ------------------ Load meteo & simulate ------------------
meteo = load_meteo(str(ROOT / "data" / "meteo_demo.csv"))
res = simulate_chauffage(client, meteo)
verdict = recommander_solution(res, client)
score = calculer_ecoscore(res)

a = res["aggregats"]
df = res["horaires"]

# ------------------ Hero ------------------
st.markdown(
    '<div class="es-card es-hero"><h1>{} — Assistant Énergie</h1><p>{}</p></div>'.format(BRAND["name"], BRAND["slogan"]),
    unsafe_allow_html=True
)
st.write("")

# ------------------ KPI Row ------------------
col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])

# Verdict/LED
if verdict.startswith("🟢"):
    LED_COLOR = C["accent"]
elif verdict.startswith("🔵"):
    LED_COLOR = C["accentAlt"]
else:
    LED_COLOR = C["warn"]

with col1:
    st.markdown(
        '<div class="es-card"><div style="display:flex; align-items:center; gap:12px;">'
        '<div class="es-led" style="color:{0}; background:{0};"></div>'
        '<div><div class="es-kpi">{1}</div><div style="color:var(--muted); font-size:13px;">COP médian observé : {2:.2f}</div></div>'
        '</div></div>'.format(LED_COLOR, verdict, a["cop_median"]),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '<div class="es-card"><div class="es-kpi">{0}<span>/100</span></div><div style="color:var(--muted); font-size:13px;">EcoScore global</div></div>'.format(score),
        unsafe_allow_html=True
    )

economie_eur = max(0.0, a["cout_gaz_eur"] - a["cout_hybride_eur"])
with col3:
    st.markdown(
        '<div class="es-card"><div class="es-kpi">{0:,.2f}<span>€ vs gaz</span></div><div style="color:var(--muted); font-size:13px;">Période simulée</div></div>'.format(economie_eur),
        unsafe_allow_html=True
    )

co2_evites = max(0.0, a["co2_gaz_kg"] - a["co2_hybride_kg"])
with col4:
    st.markdown(
        '<div class="es-card"><div class="es-kpi">{0:,.1f}<span>kg CO₂ évités</span></div><div style="color:var(--muted); font-size:13px;">Période simulée</div></div>'.format(co2_evites),
        unsafe_allow_html=True
    )

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
report = io.StringIO()
report.write("EcoSwitch Lite V3.2 — Rapport client\n")
report.write("=====================================\n\n")
report.write("Client : {} — CP {}\n".format(client.get('nom','N/A'), client.get('code_postal','')))
report.write("UA : {} W/K | T_confort : {} °C\n".format(client.get('ua_w_k'), client.get('t_confort')))
report.write("Rendement chaudière : {} | Mode tarif : {}\n".format(client.get('rendement_chaudiere'), client.get('mode_tarif')))
report.write("T_depart PAC : {} °C\n\n".format(client.get('t_depart_pac')))
report.write("Synthèse énergétique & économique\n")
report.write("---------------------------------\n")
report.write("Énergie utile demandée : {:.1f} kWh\n".format(a['energie_utile_kWh']))
report.write("COP médian observé    : {:.2f}\n\n".format(a['cop_median']))
report.write("Scénarios comparés (totaux)\n")
report.write("---------------------------\n")
report.write("Gaz seul  : coût = {:.2f} €, CO₂ = {:.1f} kg\n".format(a['cout_gaz_eur'], a['co2_gaz_kg']))
report.write("PAC seule : coût = {:.2f} €, CO₂ = {:.1f} kg\n".format(a['cout_pac_eur'], a['co2_pac_kg']))
report.write("Hybride   : coût = {:.2f} €, CO₂ = {:.1f} kg\n".format(a['cout_hybride_eur'], a['co2_hybride_kg']))
report.write("Part utile PAC en hybride : {:.1f} %\n\n".format(a['part_utile_pac_hybride_%']))
report.write("Recommandation\n")
report.write("--------------\n")
report.write("{}\n\n".format(verdict))
report.write("EcoScore (0–100)\n")
report.write("----------------\n")
report.write("{}/100\n\n".format(score))
report.write("Notes\n")
report.write("-----\n")
report.write("- Modèle Lite pédagogique. Pour une étude détaillée : EcoSwitch Core v10.2.\n")
report.write("- Hypothèses CO₂ et tarifs simplifiées. Données 100% locales, sans cloud.\n")
report.write("- « Ne devinez plus — mesurez. »\n")
report_bytes = report.getvalue().encode("utf-8")

csv_buf = io.StringIO()
df.reset_index().to_csv(csv_buf, index=False)
csv_bytes = csv_buf.getvalue().encode("utf-8")

st.download_button("📄 Télécharger le rapport client", data=report_bytes, file_name="rapport_client.txt", mime="text/plain")
st.download_button("🧾 Télécharger les résultats horaires (CSV)", data=csv_bytes, file_name="resultats_horaires.csv", mime="text/csv")
st.markdown('<a class="es-cta" href="#" onclick="window.location.reload();return false;">🔄 Actualiser l\'affichage</a>', unsafe_allow_html=True)
