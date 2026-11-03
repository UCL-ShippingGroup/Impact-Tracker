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



# ---------------------------------------------------------
# 8. Food Import Impact by Food Group
# ---------------------------------------------------------

st.subheader("Food Import Impact by Food Group")


# ---------------------------------------------------------
# 9. Select measure and scenario
# ---------------------------------------------------------

measure_food = st.segmented_control(
    "What measure of cost are you Interested in?",
    options=[
        "MTC",
        "CIF Price of Imports Relative to BAU"
    ],
    default="MTC",
    key="food_group_measure"
)

scenario_options = {
    "BAU": "bau",
    "Levy": "levy",
    "NZF as-is": "asis",
    "Brazil": "brazil",
    "LISCR": "liscr",
    "Direct": "direct"
}

scenario_food = st.segmented_control(
    "Which Scenario are you interested in?",
    options=list(scenario_options.keys()),
    default="BAU",
    key="food_group_scenario"
)

selected_scenario = scenario_options[scenario_food]


# ---------------------------------------------------------
# 10. Load selected country's datasets
# ---------------------------------------------------------

@st.cache_data
def load_food_group_data(country):

    country_path = base_url + country + "/"

    df_mtc_food = pd.read_csv(
        country_path + "food_total_costs_usd_v0.03.csv"
    )

    df_cif_food = pd.read_csv(
        country_path + "food_total_costs_pct_cif_v0.03.csv"
    )

    return df_mtc_food, df_cif_food


try:
    df_mtc_food, df_cif_food = load_food_group_data(
        country_url
    )

except Exception as e:
    st.error(
        f"Unable to load food group data for {selected_country}."
    )
    st.exception(e)
    st.stop()


# ---------------------------------------------------------
# 11. Select dataset and chart labels
# ---------------------------------------------------------

if measure_food == "MTC":

    df_food = df_mtc_food.copy()
    y_axis_title_food = "MTC (US$)"
    chart_title_food = "Food Import MTC by Food Group"

else:

    df_food = df_cif_food.copy()
    y_axis_title_food = "CIF Price of Imports Relative to BAU (%)"
    chart_title_food = "Food Import CIF Price Change by Food Group"


# ---------------------------------------------------------
# 12. Exclude total row
# ---------------------------------------------------------

df_food = df_food[
    df_food["food_group"].astype(str).str.strip().str.lower()
    != "total"
].copy()


# ---------------------------------------------------------
# 13. Reshape data from wide to long
# ---------------------------------------------------------

scenario_cols_food = df_food.columns[
    df_food.columns.str.match(r"^[A-Za-z0-9]+_\d{2,4}$")
].tolist()

df_food_long = df_food.melt(
    id_vars=["food_group"],
    value_vars=scenario_cols_food,
    var_name="Scenario_Year",
    value_name="Value"
)

# Extract scenario and year
df_food_long[["Scenario", "year"]] = (
    df_food_long["Scenario_Year"].str.rsplit(
        "_", n=1, expand=True
    )
)

# Convert year codes to full years
df_food_long["year"] = df_food_long["year"].astype(int)

df_food_long["year"] = df_food_long["year"].apply(
    lambda x: x + 2000 if x < 100 else x
)

# Ensure numeric values
df_food_long["Value"] = pd.to_numeric(
    df_food_long["Value"],
    errors="coerce"
)

df_food_long = df_food_long.dropna(
    subset=["Value"]
)


# ---------------------------------------------------------
# 14. Filter selected scenario
# ---------------------------------------------------------

df_food_plot = df_food_long[
    df_food_long["Scenario"].str.lower()
    == selected_scenario
].copy()

df_food_plot = df_food_plot.sort_values(
    ["food_group", "year"]
)


# ---------------------------------------------------------
# 15. Create Plotly line chart
# ---------------------------------------------------------

fig_food = px.line(
    df_food_plot,
    x="year",
    y="Value",
    color="food_group",
    markers=True,
    title=chart_title_food,
    labels={
        "year": "Year",
        "Value": y_axis_title_food,
        "food_group": "Food Group"
    },
    hover_data={"Value": ":,.2f"}
)

fig_food.update_traces(
    marker=dict(size=9),
    line=dict(width=2.5)
)

fig_food.update_layout(
    xaxis_title="Year",
    yaxis_title=y_axis_title_food,
    legend=dict(
        title="Food Group",
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
        b=110
    )
)

fig_food.update_xaxes(
    tickmode="array",
    tickvals=sorted(df_food_plot["year"].unique())
)

fig_food.update_yaxes(
    tickformat=",.0f"
)

st.plotly_chart(
    fig_food,
    use_container_width=True
)

