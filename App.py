import streamlit as st
import numpy as np
from scipy.stats import poisson

teams = [
    # Premier League
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Liverpool', 'Luton', 'Manchester City', 'Manchester United', 'Newcastle', 'Nottingham Forest', 'Sheffield United', 'Tottenham', 'West Ham', 'Wolves', 'Burnley',
    # Ligue 1
    'PSG', 'Marseille', 'Lyon', 'Monaco', 'Nice', 'Rennes', 'Lens', 'Lille', 'Strasbourg', 'Nantes', 'Montpellier', 'Toulouse', 'Angers', 'Brest', 'Reims', 'Metz', 'Clermont', 'Auxerre', 'Troyes', 'Lorient',
    # La Liga
    'Barcelona', 'Real Madrid', 'Atletico Madrid', 'Sevilla', 'Real Sociedad', 'Villarreal', 'Betis', 'Athletic Bilbao', 'Celta Vigo', 'Granada', 'Rayo Vallecano', 'Mallorca', 'Espanyol', 'Getafe', 'Almeria', 'Cadiz', 'Elche', 'Real Valladolid', 'Osasuna', 'Valencia',
    # Bundesliga
    'Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen', 'Wolfsburg', 'Eintracht Frankfurt', 'Union Berlin', 'Mainz', 'Freiburg', 'Hoffenheim', 'Hertha Berlin', 'FC Cologne', 'Schalke', 'Bochum', 'Augsburg', 'Stuttgart', 'Bielefeld', 'Greuther Furth', 'Darmstadt', 'Heidenheim',
    # Serie A
    'Juventus', 'Inter Milan', 'AC Milan', 'Napoli', 'Roma', 'Lazio', 'Atalanta', 'Fiorentina', 'Torino', 'Sassuolo', 'Udinese', 'Monza', 'Empoli', 'Salernitana', 'Lecce', 'Spezia', 'Verona', 'Cremonese', 'Bologna', 'Sampdoria'
]

st.title("Prédiction Score Exact Football - Grands Championnats")

home_team = st.selectbox("Équipe à domicile", teams)
away_team = st.selectbox("Équipe à l'extérieur", [team for team in teams if team != home_team])

st.markdown("### Forme récente (victoires sur 5 derniers matchs)")
home_form = st.slider("Victoires équipe domicile", 0, 5, 3)
away_form = st.slider("Victoires équipe extérieur", 0, 5, 2)

st.markdown("### Cotes bookmakers (1N2)")
cote_home = st.number_input("Cote victoire domicile", min_value=1.0, max_value=10.0, value=1.8, step=0.01)
cote_draw = st.number_input("Cote match nul", min_value=1.0, max_value=10.0, value=3.5, step=0.01)
cote_away = st.number_input("Cote victoire extérieur", min_value=1.0, max_value=10.0, value=4.0, step=0.01)

def poisson_prediction(home_form, away_form, cote_home, cote_draw, cote_away, max_goals=5):
    # Estimation lambda domicile et extérieur ajustée par forme
    base_lambda_home = 1.5 + 0.1 * (home_form - away_form)
    base_lambda_away = 1.2 + 0.1 * (away_form - home_form)

    # Calcul des probabilités scores exacts
    scores_probs = {}
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = poisson.pmf(i, base_lambda_home) * poisson.pmf(j, base_lambda_away)
            scores_probs[(i,j)] = round(prob*100, 2)

    # Score le plus probable
    most_likely = max(scores_probs, key=scores_probs.get)

    # Calcul des probabilités implicites 1N2
    prob_home = 1 / cote_home
    prob_draw = 1 / cote_draw
    prob_away = 1 / cote_away
    total = prob_home + prob_draw + prob_away
    prob_home = round(prob_home / total * 100, 1)
    prob_draw = round(prob_draw / total * 100, 1)
    prob_away = round(prob_away / total * 100, 1)

    return most_likely, scores_probs, (prob_home, prob_draw, prob_away)

if st.button("Prédire le score"):
    score, scores_probs, probs_1n2 = poisson_prediction(home_form, away_form, cote_home, cote_draw, cote_away)

    st.write(f"### Score le plus probable : {score[0]} - {score[1]}")
    st.write(f"Probabilités selon les cotes : Victoire domicile = {probs_1n2[0]}% | Match nul = {probs_1n2[1]}% | Victoire extérieur = {probs_1n2[2]}%")

    st.markdown("#### Tableau des probabilités des scores exacts (en %)")
    for i in range(6):
        row = ""
        for j in range(6):
            row += f"{i}-{j}: {scores_probs.get((i,j), 0):>5.1f}%  "
        st.text(row)
