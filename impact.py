import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')
st.title('Global Overview')
st.divider()


import streamlit as st
import pandas as pd
import plotly.express as px

from urllib.parse import quote
from urllib.error import HTTPError


# ---------------------------------------------------------
# 1. Get selected country from home page
# ---------------------------------------------------------

selected_country = st.session_state.get(
    "iso_country",
    None
)

selected_iso3 = st.session_state.get(
    "iso_3",
    None
)

selected_iso_code = st.session_state.get(
    "iso_code",
    None
)

if selected_country is None:
    st.warning("Please select a country on the home page.")
    st.stop()


# ---------------------------------------------------------
# 2. Page title
# ---------------------------------------------------------

st.title(
    f"Economic Impact of NZF Scenarios on {selected_country}"
)


# ---------------------------------------------------------
# 3. Trade flow selector
# ---------------------------------------------------------

trade_flow = st.segmented_control(
    "Which Trade flow are you interested in?",
    options=[
        "Import",
        "Export"
    ],
    default="Import",
    key="economic_trade_flow"
)


# ---------------------------------------------------------
# 4. Measure selector
# ---------------------------------------------------------

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
# 5. Map selections to country datasets
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
# 6. Load selected country's dataset
# ---------------------------------------------------------

base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/impact/"
)


@st.cache_data
def load_country_data(
    filename,
    country,
    iso3,
    iso_code
):

    # Support country-name or ISO-based folder names.
    possible_folders = [
        iso_code,
        country,
        iso3
    ]

    for folder in possible_folders:

        if folder is None:
            continue

        folder = str(folder).strip()

        url = (
            base_url
            + quote(folder, safe="")
            + "/"
            + filename
        )

        try:
            return pd.read_csv(url)

        except HTTPError as e:
            if e.code == 404:
                continue
            raise

    raise FileNotFoundError(
        f"Could not locate {filename} "
        f"for {country} in the impact directory."
    )


try:

    df = load_country_data(
        selected_file,
        selected_country,
        selected_iso3,
        selected_iso_code
    )

except (FileNotFoundError, HTTPError) as e:

    st.error(str(e))
    st.stop()


# ---------------------------------------------------------
# 7. Melt dataset from wide to long format
# ---------------------------------------------------------

years = [
    "2029", "2032", "2035", "2038",
    "2041", "2044", "2047", "2050"
]

# Ensure year columns exist
available_years = [
    year for year in years
    if year in df.columns
]

if not available_years:
    st.error("No expected year columns found in the dataset.")
    st.stop()

if "Scenario" not in df.columns:
    st.error("The dataset does not contain a Scenario column.")
    st.stop()

df_long = df.melt(
    id_vars=["Scenario"],
    value_vars=available_years,
    var_name="Year",
    value_name="Value"
)

# Convert years to integers
df_long["Year"] = df_long["Year"].astype(int)

# Convert values to numeric
df_long["Value"] = pd.to_numeric(
    df_long["Value"],
    errors="coerce"
)


# ---------------------------------------------------------
# 8. Standardise scenario names
# ---------------------------------------------------------

df_long["Scenario"] = (
    df_long["Scenario"]
    .astype(str)
    .str.strip()
    .str.strip("'\"")
)

df_long["Scenario"] = df_long["Scenario"].replace({
    "as-is": "NZF"
})

scenarios = [
    "NZF",
    "Levy",
    "Brazil",
    "LISCR",
    "Direct"
]

df_long = df_long[
    df_long["Scenario"].isin(scenarios)
].copy()

df_long = df_long.dropna(
    subset=["Value"]
)

df_long = df_long.sort_values(
    ["Scenario", "Year"]
)

if df_long.empty:
    st.warning("No data available for the selected measure.")
    st.stop()

# Prevent unintended connections between duplicate observations
if df_long.duplicated(["Scenario", "Year"]).any():
    st.error(
        "Multiple values exist for the same scenario and year. "
        "Please check the source CSV."
    )
    st.stop()


# ---------------------------------------------------------
# 9. Set y-axis based on selected measure
# ---------------------------------------------------------

if metric == "Maritime Transport Cost":

    y_axis_title = "Maritime Transport Cost (USD)"

    hover_label = "Maritime Transport Cost"

    hover_format = "$%{y:,.2f}"

    tick_format = ",.2s"

    tick_prefix = "$"

    tick_suffix = ""

else:

    if metric == "Maritime Logistics Cost":

        y_axis_title = "Maritime Logistics Cost (%)"

    elif metric == "CIF/FOB price of Imports/Exports":

        if trade_flow == "Import":
            y_axis_title = "CIF Price of Imports (%)"
        else:
            y_axis_title = "FOB Price of Exports (%)"

    else:

        y_axis_title = "MTC as % of GDP (%)"

    hover_label = y_axis_title

    hover_format = "%{y:,.2f}%"

    tick_format = ",.2f"

    tick_prefix = ""

    tick_suffix = "%"


# ---------------------------------------------------------
# 10. Create line chart
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

    labels={
        "Year": "Year",
        "Value": y_axis_title,
        "Scenario": "Scenario"
    },

    color_discrete_map={
        "NZF": "#1f77b4",
        "Levy": "#d62728",
        "Brazil": "#2ca02c",
        "LISCR": "#9467bd",
        "Direct": "#ff7f0e"
    }
)


# ---------------------------------------------------------
# 11. Custom hover formatting
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
            + hover_label + ": "
            + hover_format
            + "<extra></extra>"
        )
    )


# ---------------------------------------------------------
# 12. Chart layout
# ---------------------------------------------------------

fig.update_layout(

    height=600,

    template="plotly_white",

    hovermode="closest",

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

        ticktext=[
            "2029", "2032", "2035", "2038",
            "2041", "2044", "2047", "2050"
        ],

        range=[
            2028, 2051
        ],

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
# 13. Display chart
# ---------------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True,
    key="economic_impact_line_chart"
)

