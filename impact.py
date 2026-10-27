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


import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from urllib.parse import quote
from urllib.error import HTTPError, URLError


# ---------------------------------------------------------
# 1. Section title
# ---------------------------------------------------------

st.subheader(
    "Economic Impact Relative to BAU",
    divider="grey"
)

# Get selected country from home page
selected_country = st.session_state.get(
    "iso_country",
    None
)

if not selected_country:
    st.warning("Please select a country on the home page.")
    st.stop()


# ---------------------------------------------------------
# 2. Import / Export segmented control
# ---------------------------------------------------------

trade_flow_bar = st.segmented_control(
    "Which Trade flow are you interested in?",
    options=["Import", "Export"],
    default="Import",
    key="economic_bar_trade_flow"
)


# ---------------------------------------------------------
# 3. Dataset mapping
# ---------------------------------------------------------

dataset_map_bar = {

    "Import": {

        "Maritime Transport Cost":
            "impact_im_costs_to_bau_pct_bau_v0.64.csv",

        "Maritime Logistics Cost":
            "impact_im_costs_to_bau_pct_ciffob_v0.64.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_im_costs_to_bau_pct_cif_v0.64.csv",

        "MTC as % of GDP":
            "impact_im_costs_to_bau_pct_gdp_v0.64.csv"
    },

    "Export": {

        "Maritime Transport Cost":
            "impact_ex_costs_to_bau_pct_bau_v0.64.csv",

        "Maritime Logistics Cost":
            "impact_ex_costs_to_bau_pct_ciffob_v0.64.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_ex_costs_to_bau_pct_fob_v0.64.csv",

        "MTC as % of GDP":
            "impact_ex_costs_to_bau_pct_gdp_v0.64.csv"
    }
}


# ---------------------------------------------------------
# 4. Load country datasets
# ---------------------------------------------------------

base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/impact/"
)


@st.cache_data
def load_bar_data(country, filename):

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

    return pd.read_csv(url)


# ---------------------------------------------------------
# 5. Load, melt and combine the four datasets
# ---------------------------------------------------------

years = [
    "2029", "2032", "2035", "2038",
    "2041", "2044", "2047", "2050"
]

measures = [
    "Maritime Transport Cost",
    "Maritime Logistics Cost",
    "CIF/FOB price of Imports/Exports",
    "MTC as % of GDP"
]

all_dfs = []

for measure in measures:

    filename = dataset_map_bar[
        trade_flow_bar
    ][measure]

    try:
        df = load_bar_data(
            selected_country,
            filename
        )

    except (HTTPError, URLError, OSError) as e:

        st.error(
            f"Could not load {filename}: {e}"
        )
        st.stop()

    # Clean column names
    df.columns = (
        df.columns.astype(str).str.strip()
    )

    if "Scenario" not in df.columns:
        st.error(
            f"Scenario column missing in {filename}"
        )
        st.stop()

    available_years = [
        year for year in years
        if year in df.columns
    ]

    if not available_years:
        st.error(
            f"No year columns found in {filename}"
        )
        st.stop()

    # Melt dataset
    df_long = df.melt(
        id_vars=["Scenario"],
        value_vars=available_years,
        var_name="Year",
        value_name="Value"
    )

    # Add measure identifier
    df_long["Measure"] = measure

    all_dfs.append(df_long)


# Combine the four melted datasets
combined_df = pd.concat(
    all_dfs,
    ignore_index=True
)


# ---------------------------------------------------------
# 6. Clean data
# ---------------------------------------------------------

combined_df["Year"] = (
    combined_df["Year"].astype(int)
)

combined_df["Value"] = pd.to_numeric(
    combined_df["Value"],
    errors="coerce"
)

combined_df["Scenario"] = (
    combined_df["Scenario"]
    .astype(str)
    .str.strip()
    .str.strip("'\"")
    .str.lower()
)

scenario_lookup = {
    "as-is": "NZF",
    "nzf": "NZF",
    "levy": "Levy",
    "brazil": "Brazil",
    "liscr": "LISCR",
    "direct": "Direct"
}

combined_df["Scenario"] = (
    combined_df["Scenario"]
    .map(scenario_lookup)
)

scenarios = [
    "NZF",
    "Levy",
    "Brazil",
    "LISCR",
    "Direct"
]

# Exclude BAU and unrecognised scenarios
combined_df = combined_df[
    combined_df["Scenario"].isin(scenarios)
].copy()

combined_df = combined_df.dropna(
    subset=["Value"]
)

# Check that each measure has one value
# per scenario and year
if combined_df.duplicated(
    ["Scenario", "Year", "Measure"]
).any():

    st.error(
        "Duplicate scenario/year/measure "
        "observations found in the datasets."
    )
    st.stop()

if combined_df.empty:
    st.warning("No data available for the selected trade flow.")
    st.stop()


# ---------------------------------------------------------
# 7. Measure colours
# ---------------------------------------------------------

measure_colors = {

    "Maritime Transport Cost": "#2563eb",

    "Maritime Logistics Cost": "#e87936",

    "CIF/FOB price of Imports/Exports": "#16a085",

    "MTC as % of GDP": "#9664c7"
}


# ---------------------------------------------------------
# 8. Create five vertically arranged bar charts
# ---------------------------------------------------------

fig = make_subplots(

    rows=5,
    cols=1,

    shared_xaxes=True,

    vertical_spacing=0.07,

    subplot_titles=scenarios
)


# ---------------------------------------------------------
# 9. Add grouped bars to each scenario
# ---------------------------------------------------------

for i, scenario in enumerate(scenarios):

    scenario_df = combined_df[
        combined_df["Scenario"] == scenario
    ].copy()

    for measure in measures:

        subset = scenario_df[
            scenario_df["Measure"] == measure
        ].copy()

        subset = subset.sort_values("Year")

        fig.add_trace(

            go.Bar(

                x=subset["Year"].astype(str),

                y=subset["Value"],

                name=measure,

                marker_color=measure_colors[measure],

                offsetgroup=measure,

                legendgroup=measure,

                # Show legend only once
                showlegend=(i == 0),

                hovertemplate=(
                    "<b>" + scenario + "</b><br>"
                    + "Measure: " + measure + "<br>"
                    + "Year: %{x}<br>"
                    + "Impact relative to BAU: "
                    + "%{y:,.2f}%"
                    + "<extra></extra>"
                )
            ),

            row=i + 1,
            col=1
        )


# ---------------------------------------------------------
# 10. Common y-axis range for comparisons
# ---------------------------------------------------------

min_value = min(
    0,
    combined_df["Value"].min()
)

max_value = max(
    0,
    combined_df["Value"].max()
)

padding = max(
    (max_value - min_value) * 0.1,
    1
)

for row in range(1, 6):

    fig.update_yaxes(
        title_text="Change (%)",
        ticksuffix="%",

        range=[
            min_value - padding,
            max_value + padding
        ],

        zeroline=True,
        zerolinecolor="grey",

        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)",

        row=row,
        col=1
    )


# ---------------------------------------------------------
# 11. X-axis formatting
# ---------------------------------------------------------

year_labels = [
    "2029", "2032", "2035", "2038",
    "2041", "2044", "2047", "2050"
]

for row in range(1, 6):

    fig.update_xaxes(

        type="category",

        categoryorder="array",
        categoryarray=year_labels,

        tickmode="array",
        tickvals=year_labels,

        showgrid=False,

        row=row,
        col=1
    )

fig.update_xaxes(
    title_text="Year",
    row=5,
    col=1
)


# ---------------------------------------------------------
# 12. Overall layout
# ---------------------------------------------------------

fig.update_layout(

    height=1750,

    template="plotly_white",

    barmode="group",

    bargap=0.25,
    bargroupgap=0.03,

    hovermode="closest",

    margin=dict(
        l=80,
        r=30,
        t=80,
        b=130
    ),

    legend=dict(
        title=None,

        orientation="h",

        yanchor="top",
        y=-0.045,

        xanchor="center",
        x=0.5
    )
)


# ---------------------------------------------------------
# 13. Display figure
# ---------------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True,
    key="economic_impact_grouped_bars"
)


import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote
from urllib.error import HTTPError, URLError


# ---------------------------------------------------------
# 1. Section title and selected country
# ---------------------------------------------------------

selected_country = st.session_state.get(
    "iso_country",
    None
)

if not selected_country:
    st.warning("Please select a country on the home page.")
    st.stop()

st.subheader(
    "Economic Impact Relative to BAU",
    divider="grey"
)


# ---------------------------------------------------------
# 2. Import / Export selector
# ---------------------------------------------------------

trade_flow_bar1 = st.segmented_control(
    "Which Trade flow are you interested in?",
    options=["Import", "Export"],
    default="Import",
    key="economic_bar_trade_flow1"
)


# ---------------------------------------------------------
# 3. Cost measure selector
# ---------------------------------------------------------

metric_bar = st.segmented_control(
    "What measure of cost relative to a BAU scenario are you interested in?",
    options=[
        "Maritime Transport Cost",
        "Maritime Logistics Cost",
        "CIF/FOB price of Imports/Exports",
        "MTC as % of GDP"
    ],
    default="Maritime Transport Cost",
    key="economic_bar_metric"
)


# ---------------------------------------------------------
# 4. Dataset mapping
# ---------------------------------------------------------

dataset_map_bar = {

    "Import": {

        "Maritime Transport Cost":
            "impact_im_costs_to_bau_pct_bau_v0.64.csv",

        "Maritime Logistics Cost":
            "impact_im_costs_to_bau_pct_ciffob_v0.64.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_im_costs_to_bau_pct_cif_v0.64.csv",

        "MTC as % of GDP":
            "impact_im_costs_to_bau_pct_gdp_v0.64.csv"
    },

    "Export": {

        "Maritime Transport Cost":
            "impact_ex_costs_to_bau_pct_bau_v0.64.csv",

        "Maritime Logistics Cost":
            "impact_ex_costs_to_bau_pct_ciffob_v0.64.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_ex_costs_to_bau_pct_fob_v0.64.csv",

        "MTC as % of GDP":
            "impact_ex_costs_to_bau_pct_gdp_v0.64.csv"
    }
}

selected_file = dataset_map_bar[
    trade_flow_bar1
][metric_bar]


# ---------------------------------------------------------
# 5. Load country data
# ---------------------------------------------------------

base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/impact/"
)


@st.cache_data
def load_bar_data(country, filename):

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

    return pd.read_csv(url)


try:
    df = load_bar_data(
        selected_country,
        selected_file
    )

except (HTTPError, URLError, OSError) as e:
    st.error(f"Could not load {selected_file}: {e}")
    st.stop()


# ---------------------------------------------------------
# 6. Melt dataset
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

if "Scenario" not in df.columns or not available_years:
    st.error("Missing Scenario or year columns.")
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
# 7. Standardise scenario names
# ---------------------------------------------------------

scenario_lookup = {
    "as-is": "NZF",
    "nzf": "NZF",
    "levy": "Levy",
    "brazil": "Brazil",
    "liscr": "LISCR",
    "direct": "Direct"
}

df_long["Scenario"] = (
    df_long["Scenario"]
    .astype(str)
    .str.strip()
    .str.strip("'\"")
    .str.lower()
    .map(scenario_lookup)
)

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

if df_long.empty:
    st.warning("No data available for this selection.")
    st.stop()

if df_long.duplicated(["Scenario", "Year"]).any():
    st.error("Duplicate scenario/year observations found.")
    st.stop()


# ---------------------------------------------------------
# 8. Set scenario colours
# ---------------------------------------------------------

scenario_colors = {
    "NZF": "#1f77b4",
    "Levy": "#d62728",
    "Brazil": "#2ca02c",
    "LISCR": "#9467bd",
    "Direct": "#ff7f0e"
}


# ---------------------------------------------------------
# 9. Create grouped bar chart
# ---------------------------------------------------------

fig = px.bar(
    df_long,

    x="Year",
    y="Value",

    color="Scenario",

    barmode="group",

    category_orders={
        "Scenario": scenarios,
        "Year": list(range(2029, 2051, 3))
    },

    color_discrete_map=scenario_colors,

    labels={
        "Year": "Year",
        "Value": "Change relative to BAU (%)",
        "Scenario": "Scenario"
    },

    custom_data=["Scenario"]
)


# ---------------------------------------------------------
# 10. Hover formatting
# ---------------------------------------------------------

fig.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Year: %{x}<br>"
        "Change relative to BAU: %{y:,.2f}%"
        "<extra></extra>"
    )
)


# ---------------------------------------------------------
# 11. Chart layout
# ---------------------------------------------------------

fig.update_layout(

    height=600,

    template="plotly_white",

    barmode="group",

    bargap=0.2,
    bargroupgap=0.05,

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
        y=-0.15,
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

        range=[2027, 2052],

        showgrid=False
    ),

    yaxis=dict(
        title="Change relative to BAU (%)",

        ticksuffix="%",

        zeroline=True,
        zerolinecolor="grey",

        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)"
    )
)


# ---------------------------------------------------------
# 12. Display chart
# ---------------------------------------------------------

st.plotly_chart(
    fig,
    width='stretch',
    key="economic_impact_grouped_bars1"
)

