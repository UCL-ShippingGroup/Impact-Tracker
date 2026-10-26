import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')



from urllib.parse import quote
from urllib.error import HTTPError

# ---------------------------------------------------------
# 1. Selected country
# ---------------------------------------------------------

selected_country = st.session_state.get("iso_country", None)

if not selected_country:
    st.warning("Please select a country on the home page.")
    st.stop()

st.title(
    f"Economic Impact of NZF Scenarios on {selected_country}"
)

st.divider()

# ---------------------------------------------------------
# 2. Segmented controls
# ---------------------------------------------------------

trade_flow = st.segmented_control(
    "Which Trade flow are you interested in?",
    options=["Import", "Export"],
    default="Import",
    key="economic_trade_flow"
)

metric = st.segmented_control(
    "What measure of cost are you interested in?",
    options=[
        "Maritime Transport Cost",
        "Maritime Logistics Cost",
        "CIF/FOB price of Imports/Exports",
        "MTC as % of GDP"
    ],
    default="Maritime Transport Cost",
    key="economic_metric"
)

# ---------------------------------------------------------
# 3. Dataset mapping
# ---------------------------------------------------------

dataset_map = {
    "Import": {
        "Maritime Transport Cost":
            "impact_im_total_costs_usd_v0.64.csv",
        "Maritime Logistics Cost":
            "impact_im_total_costs_pct_ciffob_v0.64.csv",
        "CIF/FOB price of Imports/Exports":
            "impact_im_total_costs_pct_cif_v0.64.csv",
        "MTC as % of GDP":
            "impact_im_total_costs_pct_gdp_v0.64.csv"
    },
    "Export": {
        "Maritime Transport Cost":
            "impact_ex_total_costs_usd_v0.64.csv",
        "Maritime Logistics Cost":
            "impact_ex_total_costs_pct_ciffob_v0.64.csv",
        "CIF/FOB price of Imports/Exports":
            "impact_ex_total_costs_pct_fob_v0.64.csv",
        "MTC as % of GDP":
            "impact_ex_total_costs_pct_gdp_v0.64.csv"
    }
}

selected_file = dataset_map[trade_flow][metric]

# ---------------------------------------------------------
# 4. Load country data from results folder
# ---------------------------------------------------------

base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/impact/"
)

@st.cache_data
def load_country_data(country, filename):

    # Country folders use the full country name
    country_folder = quote(
        str(country).strip(),
        safe=""
    )

    url = (
        base_url
        + country_folder
        + "/results/"
        + filename
    )

    try:
        df = pd.read_csv(url)

    except HTTPError as e:
        if e.code == 404:
            raise FileNotFoundError(
                f"CSV not found at: {url}"
            ) from e
        raise

    return df


try:
    df = load_country_data(
        selected_country,
        selected_file
    )

except (FileNotFoundError, HTTPError) as e:
    st.error(str(e))
    st.stop()

# ---------------------------------------------------------
# 5. Melt dataset
# ---------------------------------------------------------

df.columns = df.columns.astype(str).str.strip()

years = [
    "2029", "2032", "2035", "2038",
    "2041", "2044", "2047", "2050"
]

available_years = [
    year for year in years
    if year in df.columns
]

if not available_years:
    st.error("No expected year columns found.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

if "Scenario" not in df.columns:
    st.error("Scenario column not found.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

df_long = df.melt(
    id_vars=["Scenario"],
    value_vars=available_years,
    var_name="Year",
    value_name="Value"
)

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

# Case-insensitive matching, retaining preferred labels
scenario_lookup = {
    "bau": "BAU",
    "as-is": "NZF",
    "nzf": "NZF",
    "levy": "Levy",
    "brazil": "Brazil",
    "liscr": "LISCR",
    "direct": "Direct"
}

df_long["Scenario"] = (
    df_long["Scenario"]
    .str.lower()
    .map(scenario_lookup)
)

# Six scenarios including BAU
scenarios = [
    "BAU",
    "NZF",
    "Levy",
    "Brazil",
    "LISCR",
    "Direct"
]

df_long = df_long[
    df_long["Scenario"].isin(scenarios)
].copy()

df_long = df_long.dropna(subset=["Value"])

df_long = df_long.sort_values(
    ["Scenario", "Year"]
)

if df_long.empty:
    st.warning("No data available for this selection.")
    st.stop()

if df_long.duplicated(["Scenario", "Year"]).any():
    st.error(
        "Duplicate scenario/year observations found. "
        "Check the selected dataset."
    )
    st.stop()

# ---------------------------------------------------------
# 7. Y-axis formatting
# ---------------------------------------------------------

if metric == "Maritime Transport Cost":

    y_axis_title = "Maritime Transport Cost (USD)"

    hover_format = "$%{y:,.2f}"

    tick_format = ",.2s"
    tick_prefix = "$"
    tick_suffix = ""

elif metric == "Maritime Logistics Cost":

    y_axis_title = "Maritime Logistics Cost (%)"

elif metric == "CIF/FOB price of Imports/Exports":

    if trade_flow == "Import":
        y_axis_title = "CIF Price of Imports (%)"
    else:
        y_axis_title = "FOB Price of Exports (%)"

else:

    y_axis_title = "MTC as % of GDP (%)"


if metric != "Maritime Transport Cost":

    hover_format = "%{y:,.2f}%"

    tick_format = ",.2f"
    tick_prefix = ""
    tick_suffix = "%"

# ---------------------------------------------------------
# 8. Scenario colours
# ---------------------------------------------------------

scenario_colors = {
    "BAU": "#444444",
    "NZF": "#1f77b4",
    "Levy": "#d62728",
    "Brazil": "#2ca02c",
    "LISCR": "#9467bd",
    "Direct": "#ff7f0e"
}

# ---------------------------------------------------------
# 9. Create line chart
# ---------------------------------------------------------

fig = px.line(
    df_long,

    x="Year",
    y="Value",

    color="Scenario",
    markers=True,

    category_orders={
        "Scenario": scenarios
    },

    color_discrete_map=scenario_colors,

    labels={
        "Year": "Year",
        "Value": y_axis_title,
        "Scenario": "Scenario"
    }
)

# ---------------------------------------------------------
# 10. Style lines, points and hover
# ---------------------------------------------------------

for trace in fig.data:

    trace.update(
        mode="lines+markers",

        line=dict(
            width=2.5
        ),

        marker=dict(
            size=8
        ),

        hovertemplate=(
            f"<b>{trace.name}</b><br>"
            "Year: %{x}<br>"
            + y_axis_title
            + ": "
            + hover_format
            + "<extra></extra>"
        )
    )

# ---------------------------------------------------------
# 11. Chart layout
# ---------------------------------------------------------

fig.update_layout(

    height=600,

    template="plotly_white",

    hovermode="closest",
    hoverdistance=5,

    margin=dict(
        l=80,
        r=30,
        t=40,
        b=90
    ),

    legend=dict(
        title=None,
        orientation="h",
        yanchor="top",
        y=-0.18,
        xanchor="center",
        x=0.5
    ),

    xaxis=dict(
        title="Year",

        tickmode="array",

        tickvals=[
            2029, 2032, 2035, 2038,
            2041, 2044, 2047, 2050
        ],

        range=[2028, 2051],

        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)"
    ),

    yaxis=dict(
        title=y_axis_title,

        tickformat=tick_format,
        tickprefix=tick_prefix,
        ticksuffix=tick_suffix,

        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)",

        zeroline=True,
        zerolinecolor="lightgrey"
    )
)

# ---------------------------------------------------------
# 12. Display chart
# ---------------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True,
    key="economic_impact_line_chart"
)



