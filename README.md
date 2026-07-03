# 📈 Options Strategy Builder

Une application **Streamlit** permettant de construire, analyser et visualiser des stratégies d'options.

L'application permet de créer des stratégies personnalisées puis d'obtenir :

- le payoff à maturité
- le P&L
- les Greeks (Delta, Gamma, Vega, Theta, Rho)
- les prix théoriques Black-Scholes
- les points morts (Break-even)
- l'exposition globale de la stratégie
- le nom de la stratégie si répértorier 

---

# Fonctionnalités

## Construction de stratégies

Création de stratégies personnalisées composées de plusieurs options :

- Calls
- Puts
- Positions Long / Short
- Quantité personnalisée
- Strike
- Prime
- Maturité
- Volatilité implicite

Jusqu'à 12 options peuvent être ajoutées.

---

# Modèle de valorisation

Les prix théoriques sont calculés avec le modèle de **Black-Scholes**.

Les Greeks calculés sont :

- Delta
- Gamma
- Vega
- Theta
- Rho

---

## Lancement 

- Ouvrir le shell et allez dans le dossier ou vous avez enregistrés app.py
- pip install -r requirements.txt
- streamlit run app.py
