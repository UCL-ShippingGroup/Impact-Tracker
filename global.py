import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')
st.title('Global Overview')

# ---------------------------------------------------------
# 1. Page title
# ---------------------------------------------------------

st.title("Maritime Trade Cost Impacts")

# ---------------------------------------------------------
# 2. Segmented controls
# ---------------------------------------------------------

trade_flow = st.segmented_control(
    "Which Trade flow are you interested in?",
    options=["Import", "Export"],
    default="Import",
    key="trade_flow"
)

cost_measure = st.segmented_control(
    "What measure of cost relative to a BAU scenario are you interested in?",
    options=[
        "Maritime Transport Cost",
        "Maritime Logistics Cost",
        "CIF/FOB price of Imports/Exports",
        "MTC as % of GDP"
    ],
    default="Maritime Transport Cost",
    key="cost_measure"
)

scenario = st.segmented_control(
    "Which Scenario would you like to view?",
    options=[
        "NZF",
        "Levy",
        "Brazil",
        "LISCR",
        "Direct"
    ],
    default="NZF",
    key="scenario"
)

# ---------------------------------------------------------
# 3. Match selections to datasets
# ---------------------------------------------------------

dataset_map = {

    "Import": {
        "Maritime Transport Cost":
            "impact_im_costs_to_bau_pct_bau_v0.64_combined.csv",

        "Maritime Logistics Cost":
            "impact_im_costs_to_bau_pct_ciffob_v0.64_combined.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_im_costs_to_bau_pct_cif_v0.64_combined.csv",

        "MTC as % of GDP":
            "impact_im_costs_to_bau_pct_gdp_v0.64_combined.csv"
    },

    "Export": {
        "Maritime Transport Cost":
            "impact_ex_costs_to_bau_pct_bau_v0.64_combined.csv",

        "Maritime Logistics Cost":
            "impact_ex_costs_to_bau_pct_ciffob_v0.64_combined.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_im_costs_to_bau_pct_fob_v0.64_combined.csv",

        "MTC as % of GDP":
            "impact_ex_costs_to_bau_pct_gdp_v0.64_combined.csv"
    }
}

selected_file = dataset_map[trade_flow][cost_measure]

# ---------------------------------------------------------
# 4. Load selected dataset
# ---------------------------------------------------------

base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/datasets/"
)

@st.cache_data
def load_data(filename):

    df = pd.read_csv(base_url + filename)

    return df


df = load_data(selected_file)

# ---------------------------------------------------------
# 5. Melt dataset from wide to long
# ---------------------------------------------------------

years = [
    "2029", "2032", "2035", "2038",
    "2041", "2044", "2047", "2050"
]

df_long = df.melt(
    id_vars=["Country", "alpha-3", "Scenario"],
    value_vars=years,
    var_name="Year",
    value_name="Value"
)

# Convert types
df_long["Year"] = df_long["Year"].astype(int)

df_long["Value"] = pd.to_numeric(
    df_long["Value"],
    errors="coerce"
)

# ---------------------------------------------------------
# 6. Standardise scenario names
# ---------------------------------------------------------

df_long["Scenario"] = (
    df_long["Scenario"]
    .astype(str)
    .str.strip()
    .str.strip("'\"")
)

# NZF is represented as 'as-is' in the source data
df_long["Scenario"] = df_long["Scenario"].replace({
    "as-is": "NZF"
})

# ---------------------------------------------------------
# 7. Filter selected scenario
# ---------------------------------------------------------

plot_df = df_long[
    df_long["Scenario"] == scenario
].copy()

plot_df = plot_df.dropna(
    subset=["alpha-3", "Value"]
)

plot_df["alpha-3"] = (
    plot_df["alpha-3"].astype(str).str.strip().str.upper()
)

# Validate records
if plot_df.empty:
    st.warning("No data available for this selection.")
    st.stop()

# Ensure each country has one value per year
if plot_df.duplicated(["alpha-3", "Year"]).any():
    st.error("Duplicate country/year records detected.")
    st.stop()

# ---------------------------------------------------------
# 8. Set fixed colour scale across all years
# ---------------------------------------------------------

min_value = min(0, plot_df["Value"].min())
max_value = plot_df["Value"].max()

if max_value <= min_value:
    max_value = min_value + 1

# ---------------------------------------------------------
# 9. Create animated choropleth map
# ---------------------------------------------------------

fig = px.choropleth(
    plot_df,

    locations="alpha-3",
    locationmode="ISO-3",

    color="Value",

    hover_name="Country",

    hover_data={
        "alpha-3": False,
        "Year": True,
        "Value": ":.2f",
        "Scenario": True
    },

    animation_frame="Year",

    category_orders={
        "Year": list(range(2029, 2051, 3))
    },

    color_continuous_scale="Reds",

    range_color=(min_value, max_value),

    labels={
        "Value": "Change (%)",
        "Year": "Year"
    },

    projection="natural earth",

    title=f"{trade_flow} - {cost_measure} - {scenario}"
)

# ---------------------------------------------------------
# 10. Map styling
# ---------------------------------------------------------

fig.update_geos(
    fitbounds="locations",
    visible=False,
    showcountries=True,
    countrycolor="white",
    showcoastlines=True,
    coastlinecolor="lightgrey",
    showland=True,
    landcolor="#f2f2f2"
)

fig.update_layout(
    height=650,

    margin=dict(
        l=0,
        r=0,
        t=60,
        b=0
    ),

    coloraxis_colorbar=dict(
        title="Change (%)",
        ticksuffix="%"
    ),

    title=dict(
        x=0.5,
        xanchor="center"
    ),

    paper_bgcolor="rgba(0,0,0,0)"
)

# ---------------------------------------------------------
# 11. Animation controls
# ---------------------------------------------------------

if fig.layout.updatemenus:

    fig.layout.updatemenus[0].buttons[0].args[1][
        "frame"
    ]["duration"] = 900

    fig.layout.updatemenus[0].buttons[0].args[1][
        "transition"
    ]["duration"] = 300

# ---------------------------------------------------------
# 12. Display map
# ---------------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": True}
)



# fig = px.choropleth(
#     plot_df,
#     locations="alpha-3",
#     locationmode="ISO-3",
#     color=selected_column,
#     hover_name='alpha-3',
#     animation_frame='year',
#     color_continuous_scale="Reds",
#     labels={selected_column: unit},
#     title=f"{chart_choice2} — {chart_choice3} — {chart_choice4} — {chart_choice}"
# )
# fig.update_layout(paper_bgcolor="white",height= 600, width=400,font_size=18)
# fig.update_geos(
#     showcoastlines=True,
#     coastlinecolor="Black",
#     #showland=True,
#     showcountries=True,
#     countrycolor="gray",
#     fitbounds="locations"
# )
# st.plotly_chart(
#     fig,
#     width='stretch'
# )
