
import pandas as pd
import streamlit as st


@st.cache_data
def load_country_iso_codes():

    country_iso_codes_c = [
        "name", "alpha-2", "alpha-3", "country-code"
    ]

    country_iso_codes_d = {
        "alpha-2": str,
        "alpha-3": str,
        "country-code": str
    }

    country_iso_codes_r = {
        "name": "iso_country",
        "alpha-2": "iso_2",
        "alpha-3": "iso_3",
        "country-code": "iso_code"
    }

    country_iso_codes = pd.read_csv(
        "https://raw.githubusercontent.com/james-stewart-808/inventory-tracker/main/datasets/country_iso_codes.csv",
        usecols=country_iso_codes_c,
        dtype=country_iso_codes_d
    ).rename(columns=country_iso_codes_r)

    # Fix Namibia ISO issue
    country_iso_codes.loc[
        country_iso_codes.iso_country == "Namibia", "iso_2"
    ] = "NA"

    country_iso_codes.loc[
        country_iso_codes.iso_country == "Congo, Democratic Republic of the",
        "iso_country"
    ] = "Democratic Republic of the Congo"

    return country_iso_codes


# Save country selection independently of the widget
def save_country_selection():
    st.session_state["selected_country"] = (
        st.session_state["_country_widget"]
    )


def country_selector():

    country_iso_codes = load_country_iso_codes()

    countries = country_iso_codes.iso_country.unique().tolist()

    # Set default country only once
    if st.session_state.get("selected_country") not in countries:
        st.session_state["selected_country"] = countries[2]

    # Restore saved selection whenever a page loads
    st.session_state["_country_widget"] = (
        st.session_state["selected_country"]
    )

    # Country selector in sidebar
    with st.sidebar:

        st.subheader("Country Selection")

        country_choice = st.selectbox(
            "Select a country",
            countries,
            key="_country_widget",
            on_change=save_country_selection
        )

    # Get ISO information for selected country
    selected_row = country_iso_codes[
        country_iso_codes.iso_country == country_choice
    ].iloc[0]

    # Update global session state variables
    st.session_state["iso_country"] = country_choice
    st.session_state["iso_2"] = selected_row["iso_2"]
    st.session_state["iso_3"] = selected_row["iso_3"]
    st.session_state["iso_code"] = selected_row["iso_code"]

