
import streamlit as st
import chardet

st.title("Debug Lecture CSV")

uploaded_file = st.file_uploader("Chargez un fichier CSV", type=["csv"])

def detect_encoding(file):
    raw = file.read(10000)
    result = chardet.detect(raw)
    file.seek(0)
    return result['encoding']

if uploaded_file:
    encoding = detect_encoding(uploaded_file)
    st.write(f"Encodage détecté : `{encoding}`")

    try:
        uploaded_file.seek(0)
        lines = uploaded_file.read().decode(encoding, errors="replace").splitlines()
        st.write(f"✅ Fichier lu avec succès : {len(lines)} lignes")
        st.code("\n".join(lines[:10]), language="text")

        # Analyse simple de longueur de ligne
        long_lines = [i for i, l in enumerate(lines) if len(l) > 1000]
        if long_lines:
            st.warning(f"Lignes très longues détectées aux index : {long_lines}")
    except Exception as e:
        st.error(f"❌ Erreur de lecture : {e}")
