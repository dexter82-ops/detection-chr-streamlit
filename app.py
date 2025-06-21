
import streamlit as st
import pandas as pd
import chardet
import re
from io import StringIO
from sklearn.feature_extraction.text import CountVectorizer

# Fonction pour détecter les faux positifs

def is_chr_match(text, keywords):
    if not isinstance(text, str):
        return False
    for kw in keywords:
        if re.search(rf'\\b{kw}\\b', text.lower()):
            return True
    return False



# Fonction pour détecter l'encodage d'un fichier
def detect_encoding(file):
    raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding'], raw_data

# Fonction pour calculer un score CHR
def compute_chr_score(row):
    score = 0
    keywords = ['café', 'restaurant', 'hôtel', 'bar', 'brasserie', 'bistrot', 'auberge']
    non_chr_keywords = ['bureau', 'siège', 'administration', 'logistique']
    urban_areas = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Bordeaux', 'Nantes', 'Lille']
    lat, lon = row.get('latitude', 0), row.get('longitude', 0)

    # Vérification des mots-clés dans le nom ou l'adresse
    combined_text = str(row.get('Nom du destinataire', '')) + ' ' + str(row.get('Adresse 1', '')) + ' ' + str(row.get('Adresse 2', ''))
    if is_chr_match(combined_text, keywords):
        score += 3
    if is_chr_match(combined_text, non_chr_keywords):
        score -= 3
    
    # if any(word in combined_text.lower() for word in keywords):
        #score += 3
    # if any(word in combined_text.lower() for word in non_chr_keywords):
        #score -= 3

    # Analyse de la ville
    if row.get('ville destinataire', '') in urban_areas:
        score += 2

    # Analyse GPS (exemple : lat/lon à Paris)
    if 48.80 < lat < 48.90 and 2.30 < lon < 2.40:
        score += 2

    return score

# Fonction de classification finale
def classify_score(score):
    if score >= 3:
        return 'CHR probable'
    elif score <= -1:
        return 'Non CHR'
    else:
        return 'Douteux'

st.title("Détection CHR Hybride")

uploaded_file = st.file_uploader("Chargez un fichier CSV", type=["csv"])
if uploaded_file:
    encoding, raw_data = detect_encoding(uploaded_file)
    data = pd.read_csv(StringIO(raw_data.decode(encoding)), sep=';')
    st.success(f"Fichier lu avec succès : {len(data)} lignes")

    # Conversion sécurisée des colonnes GPS
    data['latitude'] = pd.to_numeric(data.get('latitude', 0), errors='coerce')
    data['longitude'] = pd.to_numeric(data.get('longitude', 0), errors='coerce')

    # Calcul des scores
    data['score_CHR'] = data.apply(compute_chr_score, axis=1)
    data['identification_CHR'] = data['score_CHR'].apply(classify_score)

    st.write("Aperçu des données avec classification CHR :")
    st.dataframe(data[['Nom du destinataire', 'Adresse 1', 'Adresse 2', 'ville destinataire', 'score_CHR', 'identification_CHR']])

    # Carte interactive
    try:
        import pydeck as pdk
        map_data = data.dropna(subset=['latitude', 'longitude'])
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=48.85,
                longitude=2.35,
                zoom=10,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=map_data,
                    get_position='[longitude, latitude]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=80,
                ),
            ],
        ))
    except:
        st.warning("Carte non affichée (pydeck manquant ou données GPS incomplètes).")

    # Export
    csv_output = data.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger les résultats CSV", data=csv_output, file_name="resultat_chr_detection.csv")
