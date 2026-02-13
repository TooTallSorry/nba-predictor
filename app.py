import streamlit as st
import pandas as pd
import joblib
import json

# --- CHARGEMENT DES FICHIERS ---
# On charge le cerveau (le modèle)
model = joblib.load('nba_model.pkl')

# On charge la structure des colonnes
with open('model_columns.json', 'r') as f:
    model_columns = json.load(f)

# On charge la liste des pays connus
with open('top_countries.json', 'r') as f:
    top_countries = json.load(f)

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(page_title="NBA Predictor", page_icon="🏀")
st.title("🏀 NBA Predictor : Quel est ton niveau ?")
st.write("Entre tes statistiques actuelles pour voir ta projection en NBA.")

# Barre latérale : Paramètres physiques
st.sidebar.header("👤 Profil Physique")
age = st.sidebar.slider("Âge", 15, 45, 21)
height = st.sidebar.number_input("Taille (cm)", 150.0, 240.0, 193.0)
weight = st.sidebar.number_input("Poids (kg)", 50.0, 160.0, 85.0)

# Formulaire principal : Statistiques
st.subheader("📊 Tes Performances")
with st.form("stats_form"):
    col1, col2 = st.columns(2)
    with col1:
        gp = st.number_input("Matchs joués par saison", 1, 82, 20)
        reb = st.number_input("Rebonds (Moyenne)", 0.0, 25.0, 5.0)
        ast = st.number_input("Passes (Moyenne)", 0.0, 20.0, 2.0)
    with col2:
        usg = st.slider("Usage % (Part de ballons joués)", 0.05, 0.45, 0.20)
        ts = st.slider("True Shooting % (Efficacité)", 0.30, 0.85, 0.55)
        level = st.selectbox("Niveau de compétition actuel", 
                             ["NBA", "EuroLeague / Betclic Elite", "D1 NCAA", "Espoirs Elite (U21)", "National (NM1/NM2)", "Départemental"])

    submitted = st.form_submit_button("Calculer mon niveau NBA 🚀")

if submitted:
    # 1. Coefficients de difficulté (Translation Factors)
    coefs = {
        "NBA": 1.0, 
        "EuroLeague / Betclic Elite": 0.75,
        "D1 NCAA": 0.55, 
        "Espoirs Elite (U21)": 0.25, 
        "National (NM1/NM2)": 0.15,
        "Départemental": 0.02
    }
    current_coef = coefs[level]
    
    # 2. Préparation des données pour le modèle
    input_data = {
        'age': age, 
        'player_height': height, 
        'player_weight': weight,
        'gp': gp, 
        'reb': reb * current_coef, 
        'ast': ast * current_coef,
        'net_rating': 0.0, 
        'oreb_pct': (reb * 0.05), # Estimation simplifiée
        'dreb_pct': (reb * 0.10),
        'usg_pct': usg, 
        'ts_pct': ts, 
        'ast_pct': ast / 15, 
        'season': 2024, 
        'draft_round': 'Undrafted', 
        'country': 'France'
    }
    
    df_input = pd.DataFrame([input_data])
    
    # 3. Encodage et Alignement (Le plus important !)
    df_input['country'] = df_input['country'].apply(lambda x: x if x in top_countries else 'Other')
    df_encoded = pd.get_dummies(df_input, columns=['draft_round', 'country'])
    
    # Reindex permet de rajouter toutes les colonnes manquantes (ex: country_USA) avec des 0
    df_final = df_encoded.reindex(columns=model_columns, fill_value=0)
    
    # 4. Prédiction
    prediction = model.predict(df_final)[0]
    
    # 5. Affichage
    st.divider()
    st.balloons()
    st.success(f"### Résultat : {prediction:.2f} points / match en NBA")
    
    # Petit commentaire de scout
    if prediction > 15:
        st.write("🔥 **Verdict :** Futur All-Star potentiel.")
    elif prediction > 8:
        st.write("⭐ **Verdict :** Solide joueur de rotation NBA.")
    elif prediction > 1:
        st.write("✅ **Verdict :** Joueur de bout de banc (End of bench).")
    else:
        st.write("📉 **Verdict :** Niveau NBA non atteint. Travaille ton shoot !")