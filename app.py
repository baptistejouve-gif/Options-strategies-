# --- IMPORTS ---
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Options Strategy Builder", layout="wide")

st.title("Options Strategy Builder")
st.write("Construis et analyse des stratégies d'options : payoff, P&L, Greeks, stratégies prédéfinies.")


# --- FONCTIONS BLACK-SCHOLES ---
def d1(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        return np.nan
    return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

def bs_price(S, K, T, r, sigma, option_type):
    if T <= 0:
        return max(S - K, 0) if option_type == "Call" else max(K - S, 0)

    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)

    if option_type == "Call":
        return S * norm.cdf(d_1) - K * np.exp(-r * T) * norm.cdf(d_2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d_2) - S * norm.cdf(-d_1)

def bs_greeks(S, K, T, r, sigma, option_type):
    if T <= 0 or sigma <= 0:
        return {"Delta": 0, "Gamma": 0, "Vega": 0, "Theta": 0, "Rho": 0}

    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)

    gamma = norm.pdf(d_1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d_1) * np.sqrt(T) / 100

    if option_type == "Call":
        delta = norm.cdf(d_1)
        theta = (-S * norm.pdf(d_1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d_2)) / 365
        rho = K * T * np.exp(-r * T) * norm.cdf(d_2) / 100
    else:
        delta = norm.cdf(d_1) - 1
        theta = (-S * norm.pdf(d_1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d_2)) / 365
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d_2) / 100

    return {"Delta": delta, "Gamma": gamma, "Vega": vega, "Theta": theta, "Rho": rho}

# --- FONCTION PAYOFF ---
def option_payoff(ST, K, premium, option_type, position, quantity):
    if option_type == "Call":
        intrinsic = np.maximum(ST - K, 0)
    else:
        intrinsic = np.maximum(K - ST, 0)

    if position == "Long":
        pnl = intrinsic - premium
    else:
        pnl = premium - intrinsic

    return quantity * pnl

def sign_position(position):
    return 1 if position == "Long" else -1

# --- BIBLIOTHÈQUE DE STRATÉGIES ---
def load_strategy_preset(strategy, spot):
    K = spot
    strategies = {
        "Long Call": [["Call", "Long", K, 5.0, 1, 0.25, 0.20]],
        "Short Call": [["Call", "Short", K, 5.0, 1, 0.25, 0.20]],
        "Long Put": [["Put", "Long", K, 5.0, 1, 0.25, 0.20]],
        "Short Put": [["Put", "Short", K, 5.0, 1, 0.25, 0.20]],

        "Bull Call Spread": [["Call", "Long", 0.95*K, 7.0, 1, 0.25, 0.20], ["Call", "Short", 1.05*K, 3.0, 1, 0.25, 0.20]],
        "Bear Call Spread": [["Call", "Short", 0.95*K, 7.0, 1, 0.25, 0.20], ["Call", "Long", 1.05*K, 3.0, 1, 0.25, 0.20]],
        "Bull Put Spread": [["Put", "Short", 1.05*K, 7.0, 1, 0.25, 0.20], ["Put", "Long", 0.95*K, 3.0, 1, 0.25, 0.20]],
        "Bear Put Spread": [["Put", "Long", 1.05*K, 7.0, 1, 0.25, 0.20], ["Put", "Short", 0.95*K, 3.0, 1, 0.25, 0.20]],

        "Long Straddle": [["Call", "Long", K, 5.0, 1, 0.25, 0.20], ["Put", "Long", K, 5.0, 1, 0.25, 0.20]],
        "Short Straddle": [["Call", "Short", K, 5.0, 1, 0.25, 0.20], ["Put", "Short", K, 5.0, 1, 0.25, 0.20]],
        "Long Strangle": [["Put", "Long", 0.95*K, 3.0, 1, 0.25, 0.20], ["Call", "Long", 1.05*K, 3.0, 1, 0.25, 0.20]],
        "Short Strangle": [["Put", "Short", 0.95*K, 3.0, 1, 0.25, 0.20], ["Call", "Short", 1.05*K, 3.0, 1, 0.25, 0.20]],

        "Long Call Butterfly": [["Call", "Long", 0.90*K, 12.0, 1, 0.25, 0.20], ["Call", "Short", K, 6.0, 2, 0.25, 0.20], ["Call", "Long", 1.10*K, 2.0, 1, 0.25, 0.20]],
        "Short Call Butterfly": [["Call", "Short", 0.90*K, 12.0, 1, 0.25, 0.20], ["Call", "Long", K, 6.0, 2, 0.25, 0.20], ["Call", "Short", 1.10*K, 2.0, 1, 0.25, 0.20]],
        "Long Put Butterfly": [["Put", "Long", 0.90*K, 2.0, 1, 0.25, 0.20], ["Put", "Short", K, 6.0, 2, 0.25, 0.20], ["Put", "Long", 1.10*K, 12.0, 1, 0.25, 0.20]],
        "Short Put Butterfly": [["Put", "Short", 0.90*K, 2.0, 1, 0.25, 0.20], ["Put", "Long", K, 6.0, 2, 0.25, 0.20], ["Put", "Short", 1.10*K, 12.0, 1, 0.25, 0.20]],

        "Iron Butterfly": [["Put", "Long", 0.90*K, 2.0, 1, 0.25, 0.20], ["Put", "Short", K, 5.0, 1, 0.25, 0.20], ["Call", "Short", K, 5.0, 1, 0.25, 0.20], ["Call", "Long", 1.10*K, 2.0, 1, 0.25, 0.20]],
        "Reverse Iron Butterfly": [["Put", "Short", 0.90*K, 2.0, 1, 0.25, 0.20], ["Put", "Long", K, 5.0, 1, 0.25, 0.20], ["Call", "Long", K, 5.0, 1, 0.25, 0.20], ["Call", "Short", 1.10*K, 2.0, 1, 0.25, 0.20]],

        "Long Call Condor": [["Call", "Long", 0.85*K, 15.0, 1, 0.25, 0.20], ["Call", "Short", 0.95*K, 9.0, 1, 0.25, 0.20], ["Call", "Short", 1.05*K, 4.0, 1, 0.25, 0.20], ["Call", "Long", 1.15*K, 1.0, 1, 0.25, 0.20]],
        "Short Call Condor": [["Call", "Short", 0.85*K, 15.0, 1, 0.25, 0.20], ["Call", "Long", 0.95*K, 9.0, 1, 0.25, 0.20], ["Call", "Long", 1.05*K, 4.0, 1, 0.25, 0.20], ["Call", "Short", 1.15*K, 1.0, 1, 0.25, 0.20]],
        "Iron Condor": [["Put", "Long", 0.85*K, 1.0, 1, 0.25, 0.20], ["Put", "Short", 0.95*K, 3.0, 1, 0.25, 0.20], ["Call", "Short", 1.05*K, 3.0, 1, 0.25, 0.20], ["Call", "Long", 1.15*K, 1.0, 1, 0.25, 0.20]],
        "Reverse Iron Condor": [["Put", "Short", 0.85*K, 1.0, 1, 0.25, 0.20], ["Put", "Long", 0.95*K, 3.0, 1, 0.25, 0.20], ["Call", "Long", 1.05*K, 3.0, 1, 0.25, 0.20], ["Call", "Short", 1.15*K, 1.0, 1, 0.25, 0.20]],

        "Long Call Calendar Spread": [["Call", "Short", K, 4.0, 1, 0.10, 0.20], ["Call", "Long", K, 7.0, 1, 0.50, 0.20]],
        "Short Call Calendar Spread": [["Call", "Long", K, 4.0, 1, 0.10, 0.20], ["Call", "Short", K, 7.0, 1, 0.50, 0.20]],
        "Long Put Calendar Spread": [["Put", "Short", K, 4.0, 1, 0.10, 0.20], ["Put", "Long", K, 7.0, 1, 0.50, 0.20]],
        "Short Put Calendar Spread": [["Put", "Long", K, 4.0, 1, 0.10, 0.20], ["Put", "Short", K, 7.0, 1, 0.50, 0.20]],
        "Double Calendar Spread": [["Put", "Short", 0.95*K, 3.0, 1, 0.10, 0.20], ["Put", "Long", 0.95*K, 5.5, 1, 0.50, 0.20], ["Call", "Short", 1.05*K, 3.0, 1, 0.10, 0.20], ["Call", "Long", 1.05*K, 5.5, 1, 0.50, 0.20]],

        "Bullish Call Diagonal": [["Call", "Long", 0.95*K, 8.0, 1, 0.50, 0.20], ["Call", "Short", 1.05*K, 3.0, 1, 0.10, 0.20]],
        "Bearish Call Diagonal": [["Call", "Short", 0.95*K, 8.0, 1, 0.50, 0.20], ["Call", "Long", 1.05*K, 3.0, 1, 0.10, 0.20]],
        "Bullish Put Diagonal": [["Put", "Short", 1.05*K, 8.0, 1, 0.50, 0.20], ["Put", "Long", 0.95*K, 3.0, 1, 0.10, 0.20]],
        "Bearish Put Diagonal": [["Put", "Long", 1.05*K, 8.0, 1, 0.50, 0.20], ["Put", "Short", 0.95*K, 3.0, 1, 0.10, 0.20]],

        "Call Ratio Spread 1x2": [["Call", "Long", 0.95*K, 7.0, 1, 0.25, 0.20], ["Call", "Short", 1.05*K, 3.0, 2, 0.25, 0.20]],
        "Put Ratio Spread 1x2": [["Put", "Long", 1.05*K, 7.0, 1, 0.25, 0.20], ["Put", "Short", 0.95*K, 3.0, 2, 0.25, 0.20]],
        "Call Backspread 1x2": [["Call", "Short", 0.95*K, 7.0, 1, 0.25, 0.20], ["Call", "Long", 1.05*K, 3.0, 2, 0.25, 0.20]],
        "Put Backspread 1x2": [["Put", "Short", 1.05*K, 7.0, 1, 0.25, 0.20], ["Put", "Long", 0.95*K, 3.0, 2, 0.25, 0.20]],

        "Synthetic Long Forward": [["Call", "Long", K, 5.0, 1, 0.25, 0.20], ["Put", "Short", K, 5.0, 1, 0.25, 0.20]],
        "Synthetic Short Forward": [["Call", "Short", K, 5.0, 1, 0.25, 0.20], ["Put", "Long", K, 5.0, 1, 0.25, 0.20]],

        "Protective Put": [["Put", "Long", 0.95*K, 3.0, 1, 0.25, 0.20]],
        "Covered Call": [["Call", "Short", 1.05*K, 3.0, 1, 0.25, 0.20]],
        "Collar": [["Put", "Long", 0.95*K, 3.0, 1, 0.25, 0.20], ["Call", "Short", 1.05*K, 3.0, 1, 0.25, 0.20]],
        "Zero Cost Collar": [["Put", "Long", 0.95*K, 3.0, 1, 0.25, 0.20], ["Call", "Short", 1.08*K, 3.0, 1, 0.25, 0.20]],

        "Long Guts": [["Call", "Long", 0.95*K, 7.0, 1, 0.25, 0.20], ["Put", "Long", 1.05*K, 7.0, 1, 0.25, 0.20]],
        "Short Guts": [["Call", "Short", 0.95*K, 7.0, 1, 0.25, 0.20], ["Put", "Short", 1.05*K, 7.0, 1, 0.25, 0.20]],

        "Bull Call Ladder": [["Call", "Long", 0.95*K, 8.0, 1, 0.25, 0.20], ["Call", "Short", 1.05*K, 4.0, 1, 0.25, 0.20], ["Call", "Short", 1.15*K, 2.0, 1, 0.25, 0.20]],
        "Bear Put Ladder": [["Put", "Long", 1.05*K, 8.0, 1, 0.25, 0.20], ["Put", "Short", 0.95*K, 4.0, 1, 0.25, 0.20], ["Put", "Short", 0.85*K, 2.0, 1, 0.25, 0.20]],
    }
    return strategies.get(strategy, [])

strategy_list = ["Custom", "Long Call", "Short Call", "Long Put", "Short Put", "Bull Call Spread", "Bear Call Spread", "Bull Put Spread", "Bear Put Spread", "Long Straddle", "Short Straddle", "Long Strangle", "Short Strangle", "Long Call Butterfly", "Short Call Butterfly", "Long Put Butterfly", "Short Put Butterfly", "Iron Butterfly", "Reverse Iron Butterfly", "Long Call Condor", "Short Call Condor", "Iron Condor", "Reverse Iron Condor", "Long Call Calendar Spread", "Short Call Calendar Spread", "Long Put Calendar Spread", "Short Put Calendar Spread", "Double Calendar Spread", "Bullish Call Diagonal", "Bearish Call Diagonal", "Bullish Put Diagonal", "Bearish Put Diagonal", "Call Ratio Spread 1x2", "Put Ratio Spread 1x2", "Call Backspread 1x2", "Put Backspread 1x2", "Synthetic Long Forward", "Synthetic Short Forward", "Protective Put", "Covered Call", "Collar", "Zero Cost Collar", "Long Guts", "Short Guts", "Bull Call Ladder", "Bear Put Ladder"]

# --- INTERPRÉTATION DES GREEKS ---
def greek_exposure_comment(name, value):
    if abs(value) < 1e-6:
        return f"Neutral {name.lower()}"
    return f"Long {name.lower()}" if value > 0 else f"Short {name.lower()}"

# --- PARAMÈTRES UTILISATEUR ---
st.sidebar.header("Paramètres globaux")

spot = st.sidebar.number_input("Spot actuel", min_value=1.0, value=100.0, step=1.0)
risk_free_rate = st.sidebar.number_input("Taux sans risque r", min_value=-0.10, max_value=0.30, value=0.03, step=0.005, format="%.3f")

price_min = st.sidebar.number_input("Prix min affiché", min_value=0.0, value=50.0, step=5.0)
price_max = st.sidebar.number_input("Prix max affiché", min_value=1.0, value=150.0, step=5.0)

selected_ST = st.sidebar.slider("Prix du sous-jacent à maturité", min_value=float(price_min), max_value=float(price_max), value=float(spot), step=1.0)
preset = st.sidebar.selectbox("Stratégie prédéfinie", strategy_list)

if preset == "Custom":
    preset_data = []
    number_options = st.sidebar.number_input("Nombre d'options", min_value=1, max_value=12, value=2, step=1)
else:
    preset_data = load_strategy_preset(preset, spot)
    number_options = len(preset_data)

# --- CONSTRUCTION DES JAMBES ---
st.markdown("### Construction de la stratégie")

options = []

for i in range(int(number_options)):
    st.markdown(f"#### Jambe {i + 1}")

    default = preset_data[i] if preset_data else ["Call", "Long", spot, 5.0, 1, 0.25, 0.20]
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        option_type = st.selectbox("Type", ["Call", "Put"], index=["Call", "Put"].index(default[0]), key=f"type_{i}")
    with col2:
        position = st.selectbox("Position", ["Long", "Short"], index=["Long", "Short"].index(default[1]), key=f"position_{i}")
    with col3:
        strike = st.number_input("Strike", min_value=1.0, value=float(default[2]), step=1.0, key=f"strike_{i}")
    with col4:
        premium = st.number_input("Prime", min_value=0.0, value=float(default[3]), step=0.5, key=f"premium_{i}")
    with col5:
        quantity = st.number_input("Quantité", min_value=1, value=int(default[4]), step=1, key=f"quantity_{i}")
    with col6:
        maturity = st.number_input("Maturité T", min_value=0.001, value=float(default[5]), step=0.05, key=f"maturity_{i}")
    with col7:
        implied_vol = st.number_input("Vol implicite", min_value=0.001, value=float(default[6]), step=0.01, key=f"vol_{i}")

    theo_price = bs_price(spot, strike, maturity, risk_free_rate, implied_vol, option_type)
    greeks = bs_greeks(spot, strike, maturity, risk_free_rate, implied_vol, option_type)
    multiplier = sign_position(position) * quantity

    options.append({"Type": option_type, "Position": position, "Strike": strike, "Prime": premium, "Quantité": quantity, "Maturité": maturity, "Vol": implied_vol, "Prix BS": theo_price, "Delta": greeks["Delta"] * multiplier, "Gamma": greeks["Gamma"] * multiplier, "Vega": greeks["Vega"] * multiplier, "Theta": greeks["Theta"] * multiplier, "Rho": greeks["Rho"] * multiplier})

# --- CALCUL DU PAYOFF ET DES GREEKS ---
ST_range = np.linspace(price_min, price_max, 700)
total_pnl = np.zeros_like(ST_range)

for opt in options:
    total_pnl += option_payoff(ST_range, opt["Strike"], opt["Prime"], opt["Type"], opt["Position"], opt["Quantité"])

selected_pnl = np.interp(selected_ST, ST_range, total_pnl)

total_delta = sum(o["Delta"] for o in options)
total_gamma = sum(o["Gamma"] for o in options)
total_vega = sum(o["Vega"] for o in options)
total_theta = sum(o["Theta"] for o in options)
total_rho = sum(o["Rho"] for o in options)

net_premium = sum(o["Prime"] * o["Quantité"] * (1 if o["Position"] == "Long" else -1) for o in options)

breakeven_indices = np.where(np.diff(np.sign(total_pnl)) != 0)[0]
breakevens = []

for idx in breakeven_indices:
    x1, x2 = ST_range[idx], ST_range[idx + 1]
    y1, y2 = total_pnl[idx], total_pnl[idx + 1]
    if y2 != y1:
        breakevens.append(x1 - y1 * (x2 - x1) / (y2 - y1))

# --- AFFICHAGE DES RÉSULTATS ---
st.markdown("### Résumé de la stratégie")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Stratégie", preset)
col2.metric("P&L au prix choisi", f"{selected_pnl:.2f}")
col3.metric("Prime nette", f"{net_premium:.2f}")
col4.metric("Prix final choisi", f"{selected_ST:.2f}")

col5, col6, col7 = st.columns(3)

col5.metric("Gain max zone affichée", f"{np.max(total_pnl):.2f}")
col6.metric("Perte max zone affichée", f"{np.min(total_pnl):.2f}")
col7.metric("Breakeven(s)", ", ".join([f"{x:.2f}" for x in breakevens]) if breakevens else "Aucun")

# --- GRAPHIQUE INTERACTIF DU PAYOFF ---
st.markdown("### Payoff / P&L à maturité")

fig_payoff = go.Figure()
fig_payoff.add_trace(go.Scatter(x=ST_range, y=total_pnl, mode="lines", name="P&L total"))
fig_payoff.add_hline(y=0, line_dash="dash", annotation_text="P&L = 0")
fig_payoff.add_vline(x=selected_ST, line_dash="dot", annotation_text=f"S_T = {selected_ST:.2f}")
fig_payoff.update_layout(title="P&L de la stratégie à maturité", xaxis_title="Prix du sous-jacent à maturité", yaxis_title="Profit / Perte", hovermode="x unified", height=600)

st.plotly_chart(fig_payoff, use_container_width=True)

# --- AFFICHAGE DES GREEKS ---
st.markdown("### Exposition aux Greeks")

g1, g2, g3, g4, g5 = st.columns(5)

g1.metric("Delta", f"{total_delta:.4f}")
g2.metric("Gamma", f"{total_gamma:.4f}")
g3.metric("Vega", f"{total_vega:.4f}")
g4.metric("Theta", f"{total_theta:.4f}")
g5.metric("Rho", f"{total_rho:.4f}")

st.markdown("### Interprétation")

st.write(greek_exposure_comment("Delta", total_delta))
st.write(greek_exposure_comment("Gamma", total_gamma))
st.write(greek_exposure_comment("Vega", total_vega))
st.write(greek_exposure_comment("Theta", total_theta))
st.write(greek_exposure_comment("Rho", total_rho))

if total_gamma > 0 and total_vega > 0 and total_theta < 0:
    st.info("Profil long convexité : long gamma, long vega, short theta.")
elif total_gamma < 0 and total_vega < 0 and total_theta > 0:
    st.info("Profil vendeur de volatilité : short gamma, short vega, long theta.")
elif total_delta > 0:
    st.info("Profil directionnel haussier.")
elif total_delta < 0:
    st.info("Profil directionnel baissier.")
else:
    st.info("Profil globalement delta-neutre autour du spot actuel.")

# --- TABLEAU DÉTAILLÉ DES JAMBES ---
with st.expander("Voir le détail des jambes"):
    df_options = pd.DataFrame(options)
    st.dataframe(df_options.style.format({"Strike": "{:.2f}", "Prime": "{:.2f}", "Maturité": "{:.2f}", "Vol": "{:.2%}", "Prix BS": "{:.2f}", "Delta": "{:.4f}", "Gamma": "{:.4f}", "Vega": "{:.4f}", "Theta": "{:.4f}", "Rho": "{:.4f}"}), use_container_width=True)

# --- NOTE MÉTHODOLOGIQUE ---
st.warning("Attention : pour les calendar et diagonal spreads, le payoff affiché est une approximation simplifiée. La vraie valeur doit être calculée en mark-to-market avant maturité avec Black-Scholes.")
