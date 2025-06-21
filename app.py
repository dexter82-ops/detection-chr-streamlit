
import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Détection CHR", layout="wide")

st.title("Détection des établissements CHR (Cafés, Hôtels, Restaurants)")
st.markdown("Uploadez un fichier CSV contenant au minimum : `Nom du destinataire`, `Adresse 1`, `Adresse 2`, `Latitude`, `Longitude`.")

# Mots-clés CHR
chr_keywords = {
    "restaurant": ["restaurant", "resto", "pizzeria", "brasserie", "crêperie", "snack"],
    "hôtel": ["hotel", "hôtel", "hostel", "auberge"],
    "bar": ["bar", "pub", "café", "bistrot", "taverne"]
}

def detect_chr_keywords(text):
    text = str(text).lower()
    for category, keywords in chr_keywords.items():
        for kw in keywords:
            if kw in text:
                return category.capitalize()
    return None

def get_place_type_osm(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "zoom": 18,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "CHR-Detection-App"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if 'type' in data:
            osm_type = data['type']
            if osm_type in ['restaurant', 'cafe', 'bar', 'pub', 'fast_food']:
                return "Restaurant" if osm_type == 'restaurant' else "Café / Bar"
            elif osm_type in ['hotel', 'motel', 'hostel', 'guest_house']:
                return "Hôtel / Hébergement"
            else:
                return osm_type
        return "inconnu"
    except:
        return "erreur"

uploaded_file = st.file_uploader("Déposer un fichier CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    st.write("Aperçu des données :", df.head())

    if st.button("Lancer l’analyse CHR"):
        results = []
        for index, row in df.iterrows():
            texte = f"{row.get('Nom du destinataire', '')} {row.get('Adresse 1 destinataire', '')} {row.get('Adresse 2 destinataire', '')}"
            detection_texte = detect_chr_keywords(texte)

            if pd.notna(row.get("Latitude")) and pd.notna(row.get("Longitude")):
                detection_gps = get_place_type_osm(row["Latitude"], row["Longitude"])
            else:
                detection_gps = None

            if detection_texte:
                final_result = detection_texte
            elif detection_gps in ["Restaurant", "Café / Bar", "Hôtel / Hébergement"]:
                final_result = detection_gps
            else:
                final_result = "Non CHR"

            results.append(final_result)
            time.sleep(1)  # respecter limites API

        df["Type CHR Détecté"] = results
        st.success("Analyse terminée.")
        st.dataframe(df)

        # Télécharger
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger les résultats (CSV)", csv, "résultat_CHR.csv", "text/csv")
