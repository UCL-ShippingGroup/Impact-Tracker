import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# ---------------------------------------------------------
# 1. Page title and selected country
# ---------------------------------------------------------

st.title("Food Import Impact")

selected_country = st.session_state.get("iso_country", None)

if selected_country is None:
    st.warning("Please select a country on the Home page.")
    st.stop()

st.subheader(f"Food Import Impact: {selected_country}")


# ---------------------------------------------------------
# 2. Select measure
# ---------------------------------------------------------

measure = st.segmented_control(
    "What measure of cost are you Interested in?",
    options=[
        "MTC",
        "CIF Price of Imports Relative to BAU"
    ],
    default="MTC",
    key="food_impact_measure"
)


# ---------------------------------------------------------
# 3. Load selected country's datasets
# ---------------------------------------------------------

base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/food/"
)

country_url = quote(selected_country, safe="")

@st.cache_data
def load_food_data(country):

    country_path = base_url + country + "/"

    df_mtc = pd.read_csv(
        country_path + "food_total_costs_usd_tot_v0.03.csv"
    )

    df_cif = pd.read_csv(
        country_path + "food_total_costs_pct_cif_tot_v0.03.csv"
    )

    return df_mtc, df_cif


try:
    df_mtc, df_cif = load_food_data(country_url)

except Exception as e:
    st.error(f"Unable to load food data for {selected_country}.")
    st.exception(e)
    st.stop()


# ---------------------------------------------------------
# 4. Select dataset and axis labels
# ---------------------------------------------------------

if measure == "MTC":

    df = df_mtc.copy()
    y_axis_title = "MTC (US$)"
    chart_title = "Total Food Import MTC by Scenario"

else:

    df = df_cif.copy()
    y_axis_title = "CIF Price of Imports Relative to BAU (%)"
    chart_title = "Food Import CIF Price Change by Scenario"


# ---------------------------------------------------------
# 5. Filter for total food impact only
# ---------------------------------------------------------

df = df[
    df["food_group"].astype(str).str.strip().str.lower()
    == "total"
].copy()

if df.empty:
    st.warning("No total food impact data available.")
    st.stop()


# ---------------------------------------------------------
# 6. Reshape data from wide to long
# ---------------------------------------------------------

# Identify scenario/year columns
scenario_cols = df.columns[
    df.columns.str.match(r"^[A-Za-z0-9]+_\d{2,4}$")
].tolist()

if not scenario_cols:
    st.error("No scenario/year columns found.")
    st.stop()

df_long = df[scenario_cols].melt(
    var_name="Scenario_Year",
    value_name="Value"
)

# Extract scenario and year
df_long[["Scenario", "year"]] = (
    df_long["Scenario_Year"].str.rsplit(
        "_", n=1, expand=True
    )
)

# Convert year codes to full years
df_long["year"] = df_long["year"].astype(int)

df_long["year"] = df_long["year"].apply(
    lambda x: x + 2000 if x < 100 else x
)

# Scenario names
scenario_names = {
    "bau": "BAU",
    "levy": "Levy",
    "asis": "As Is",
    "brazil": "Brazil",
    "liscr": "LISCR",
    "direct": "Direct"
}

df_long["Scenario"] = (
    df_long["Scenario"]
    .str.lower()
    .map(scenario_names)
    .fillna(df_long["Scenario"].str.upper())
)

# Ensure numeric values
df_long["Value"] = pd.to_numeric(
    df_long["Value"],
    errors="coerce"
)

df_long = df_long.dropna(subset=["Value"])

df_long = df_long.sort_values(
    ["Scenario", "year"]
)


# ---------------------------------------------------------
# 7. Create line chart
# ---------------------------------------------------------

fig = px.line(
    df_long,
    x="year",
    y="Value",
    color="Scenario",
    markers=True,
    title=chart_title,
    labels={
        "year": "Year",
        "Value": y_axis_title,
        "Scenario": "Scenario"
    }
)

fig.update_traces(
    marker=dict(size=9),
    line=dict(width=2.5)
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title=y_axis_title,
    legend=dict(
        title="Scenario",
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=90
    )
)

fig.update_xaxes(
    tickmode="array",
    tickvals=sorted(df_long["year"].unique())
)

st.plotly_chart(
    fig,
    use_container_width=True
)
