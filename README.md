## 📈 Options Strategy Builder

A **Streamlit** application for building, analyzing, and visualizing options strategies.

The application allows users to create custom option strategies and provides:

- Payoff at expiration
- Profit & Loss (P&L)
- Greeks (Delta, Gamma, Vega, Theta, Rho)
- Theoretical Black-Scholes prices
- Break-even points
- Overall strategy exposure
- Strategy name if it matches a predefined strategy

# Features
Create custom strategies composed of multiple option legs:

- Calls
- Puts
- Long / Short positions
- Custom quantity
- Strike
- Premium
- Time to maturity
- Implied volatility
Up to **12 option legs** can be added.

# Pricing Model

Theoretical option prices are calculated using the **Black-Scholes** model.
The calculated Greeks include:

- Delta
- Gamma
- Vega
- Theta
- Rho

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```
## Author

Baptiste Jouve
