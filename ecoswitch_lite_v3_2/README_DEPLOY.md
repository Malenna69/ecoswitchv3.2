# Déploiement en ligne — EcoSwitch Lite V3.2

## Option A — Streamlit Community Cloud (gratuit)
1. Créez un dépôt GitHub et poussez tout le dossier.
2. Allez sur https://share.streamlit.io → **New app** → choisissez votre repo.
3. App file: `streamlit_app.py` (par défaut) → Deploy.

## Option B — Hugging Face Spaces (gratuit)
1. Créez un Space → type **Streamlit**.
2. Uploadez tous les fichiers (ou connectez votre repo GitHub).
3. Fichier d'entrée: `streamlit_app.py`.

## Option C — Render (gratuit)
1. Connectez un repo via Dashboard Render → **New Web Service**.
2. Le fichier `render.yaml` est déjà prêt (build/start). Port auto.

## Option D — Docker / VPS
```bash
docker build -t ecoswitch-lite .
docker run -p 8501:8501 ecoswitch-lite
```

## Variables utiles
- Aucune variable requise. Tout est local.
- Pour la prod, vous pourrez pointer vers de vraies données météo/tarifs.
