
import streamlit as st
import pandas as pd
import chardet

# Détection automatique de l'encodage
def detect_encoding(file):
    raw = file.read(10000)
    result = chardet.detect(raw)
    file.seek(0)
    return result['encoding']

# Lecture CSV avec essais multiples de séparateurs
def read_csv_with_guess(file):
    encoding = detect_encoding(file)
    separators = [';', ',', '\t']
    for sep in separators:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding, sep=sep)
            if df.shape[1] > 1:
                return df, encoding, sep
        except Exception as e:
            continue
    return None, encoding, None

st.title("Détection CHR (Cafés, Hôtels, Restaurants)")
uploaded_file = st.file_uploader("Chargez un fichier CSV", type=["csv"])

if uploaded_file:
    df, encoding, sep = read_csv_with_guess(uploaded_file)

    if df is None:
        st.error(f"❌ Échec de lecture du fichier CSV. Encodage détecté : {encoding}. Essayez de sauvegarder en CSV UTF-8.")
    else:
        st.success(f"✅ Fichier chargé avec succès. Encodage: {encoding}, Séparateur détecté: '{sep}'")
        st.write("Aperçu des données :", df.head())
        # Tu peux ici ajouter l'appel à la fonction de détection CHR + affichage
