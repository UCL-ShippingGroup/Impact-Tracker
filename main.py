import pandas as pd
import requests
from io import StringIO
import streamlit as st

# Load Country ISO data
country_iso_codes_c = ["name", "alpha-2", "alpha-3", "country-code"]
country_iso_codes_d = {"alpha-2":str, "alpha-3":str, "country-code":str}
country_iso_codes_r = {"name":"iso_country", "alpha-2":"iso_2", "alpha-3":"iso_3", "country-code":"iso_code"}

country_iso_codes = pd.read_csv(
  "https://raw.githubusercontent.com/james-stewart-808/inventory-tracker/main/datasets/country_iso_codes.csv",
  usecols=country_iso_codes_c, 
  dtype=country_iso_codes_d).rename(
  columns=country_iso_codes_r)

# Fix Namibia ISO issue
country_iso_codes.loc[country_iso_codes.iso_country == "Namibia", "iso_2"] = "NA"
country_iso_codes.loc[country_iso_codes.iso_country == "Congo, Democratic Republic of the", "iso_country"] = "Democratic Republic of the Congo"


# Homepage Description
st.title("The NZF Impact Tracker")


st.subheader("Country selection", divider = 'grey')

# Country Selector
country_choice = st.selectbox(
    "For which country would you like statistics on international shipping activity and emissions? Ensure a country is selected before moving on to the following pages.",
    country_iso_codes.iso_country.unique(),
    index=2)

# set as global variable
st.session_state.iso_country = country_choice
st.session_state.iso_2 = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_2.values[0]
st.session_state.iso_3 = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_3.values[0]
st.session_state.iso_code = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_code.values[0]

#st.write("""Use the sidebar to explore the different components of the dashboard...""")
#st.page_link("inventories.py", label="**Voyage-based Inventories**", icon="🚢")
#st.page_link("trade.py", label="**Merchandise Trade Portfolios**", icon="📦")

st.divider()


st.markdown(
"""
##### Disclaimer

The content on this website is for informational and educational purposes only. It should not be considered as \
financial, investment, or legal advice. We are not financial advisors, and the information provided is not a substitute \
for professional advice from a qualified expert who is aware of your individual circumstances. Always conduct your own \
research and consult with a licensed financial professional before making any investment or financial decisions. Any \
reliance you place on the information provided on this site is strictly at your own risk. We are not liable for any \
losses or damages incurred from the use of this information.
"""
)
#st.divider()



#st.markdown("##### References")

#st.write(
#"""
#IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories. \
#    Volume 2 (Energy), Chapter 3 on Mobile combustion – Section 5 on Water-borne \
#    Navigation. Intergovernmental Panel on Climate Change.
#"""
#)
