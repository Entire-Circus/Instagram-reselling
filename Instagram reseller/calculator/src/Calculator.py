import streamlit as st
import math
import requests

st.set_page_config(page_title="Price Calculator (CAD/USD)", layout="centered")
st.title("Price Calculator (CAD/USD)")

@st.cache_data(show_spinner=False)
def get_exchange_rate(base="USD", target="CAD", api_key="YOUR_API_KEY_HERE"):
    allowed = {"CAD", "USD"}
    if base not in allowed or target not in allowed:
        st.error("Only CAD and USD are supported.")
        return None
    if base == target:
        return 1.0

    url = f"https://open.er-api.com/v6/latest/{base}"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("result") == "success" and "rates" in data:
            rates = data["rates"]
            if target in rates:
                return rates[target]
            else:
                st.error(f"Target currency '{target}' not found in rates.")
                return None
        else:
            st.error(f"Unexpected API response: {data}")
            return None

    except Exception as e:
        st.error(f"Failed to fetch exchange rate for {base} → {target}: {e}")
        return None

# Sidebar inputs
st.sidebar.header("Input Parameters")

base_currency = st.sidebar.selectbox("Base Price Currency", ["CAD", "USD"])
base_price = st.sidebar.number_input(f"Base Price (in {base_currency})", min_value=0.0, step=0.01, value=100.0)

delivery_way = st.sidebar.selectbox("Delivery Way", ["Air", "Sea"])
include_delivery = st.sidebar.checkbox("Include Delivery Cost", value=True)

ad_price_usd = st.sidebar.number_input("Ad Price (in USD)", min_value=0.0, step=0.01, value=5.0)
include_ads = st.sidebar.checkbox("Include Advertising Cost", value=True)

markup_percent = st.sidebar.number_input("Markup (%)", min_value=0.0, step=0.01, value=0.0)

target_currency = st.sidebar.selectbox("Convert Final Price To", ["USD", "CAD"])

st.sidebar.write("Weight Inputs")
real_weight = st.sidebar.number_input("Real weight (kg)", min_value=0.0, step=0.01, value=0.0)

st.sidebar.write("Formula weight")
length = st.sidebar.number_input("Length (cm)", min_value=0.0, step=0.01, value=0.0)
width = st.sidebar.number_input("Width (cm)", min_value=0.0, step=0.01, value=0.0)
height = st.sidebar.number_input("Height (cm)", min_value=0.0, step=0.01, value=0.0)

# Fetch exchange rates
API_KEY = "cf5d8f6a9b86c63a5aaf8c29"
rate_base_to_target = (
    1.0 if base_currency == target_currency else get_exchange_rate(base_currency, target_currency, API_KEY)
)
rate_cad_to_target = (
    1.0 if target_currency == "CAD" else get_exchange_rate("CAD", target_currency, API_KEY)
)
rate_usd_to_target = (
    1.0 if target_currency == "USD" else get_exchange_rate("USD", target_currency, API_KEY)
)

if None in [rate_base_to_target, rate_cad_to_target, rate_usd_to_target]:
    st.stop()

# Convert all inputs to target currency
base_converted = base_price * rate_base_to_target
ad_converted = ad_price_usd * rate_usd_to_target

# Tax (12%)
tax_rate = 0.12
tax_amount = base_converted * tax_rate
price_with_tax = base_converted + tax_amount

# Apply markup after tax
markup_amount = price_with_tax * (markup_percent / 100)
price_with_markup = price_with_tax + markup_amount

# Delivery calculation
formula_weight = length * width * height / 500
weight = max(formula_weight, real_weight)
charged_weight = math.ceil(weight)

if delivery_way == "Air":
    delivery_cost = charged_weight * 8.45 + 15
elif delivery_way == "Sea":
    delivery_cost = charged_weight * 4.45 + 15

delivery_converted = delivery_cost * rate_cad_to_target if include_delivery else 0.0
ad_converted = ad_converted if include_ads else 0.0

# Final price
final_price = price_with_markup + delivery_converted + ad_converted

# Show breakdown
st.subheader("Input Summary")
st.markdown(f"- Base Price: **{base_price:.2f} {base_currency}** → {base_converted:.2f} {target_currency}")
st.markdown(f"- Tax (12%): +{tax_amount:.2f} {target_currency} → **{price_with_tax:.2f} {target_currency}**")
st.markdown(f"- Markup: **{markup_percent}%** → +{markup_amount:.2f} {target_currency}")
st.markdown(f"- Price after Markup (before Delivery & Ads): **{price_with_markup:.2f} {target_currency}**")
st.markdown(f"- Real weight: {real_weight} kg")
st.markdown(f"- Formula weight: {formula_weight:.2f} kg")

if include_delivery:
    st.markdown(f"- Delivery Price: **{delivery_cost:.2f} CAD** → {delivery_converted:.2f} {target_currency}")
else:
    st.markdown("- Delivery Price: **Excluded**")

if include_ads:
    st.markdown(f"- Advertising Cost: **{ad_price_usd:.2f} USD** → {ad_converted:.2f} {target_currency}")
else:
    st.markdown("- Advertising Cost: **Excluded**")

st.markdown("---")
st.markdown(f"### Final Price: `{final_price:.2f} {target_currency}`")
