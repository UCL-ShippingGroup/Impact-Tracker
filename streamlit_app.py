import streamlit as st
import pandas as pd

# logo at the top of sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"]::before {
        content: "";
        display: block;
        margin: 0px auto 20px auto;
        height: 120px;
        width: 180px;
        background-image: url(https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/UCL_Logo_S_1C_B_RGB_Energy-Inst.png);
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define the pages
main = st.Page("main.py", title="Overview", icon="🏡")
globa = st.Page("global.py", title="Global Overview", icon="🌏")
#regional = st.Page("regional.py", title="Regional Overview", icon="🗺️")
#inventories = st.Page("inventories.py", title="Voyage Inventories", icon="🚢")
#trade = st.Page("trade.py", title="Seaborne Trade Portfolios", icon="📦")
impact_tracking = st.Page("impact.py", title="NZF Economic Impacts", icon="💵")
#costs_of_climate_change = st.Page("costs_of_climate_change.py", title="Costs of Climate Change", icon="💰")
#contact = st.Page("contact.py", title="Contact", icon="📒")

# Set up navigation
pg = st.navigation([main, globa, impact])

# Run the selected page
pg.run()
