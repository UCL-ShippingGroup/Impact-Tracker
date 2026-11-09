import streamlit as st
import pandas as pd
import plotly.express as px

import streamlit as st
from country_selector import country_selector

# Country selector in sidebar
country_selector()
st.set_page_config(layout='wide')
# Homepage
st.title("The Net-Zero Framework (NZF) Impact Tracker")
st.subheader("Overview",
            divider='grey')

st.write(
         """   
            The NZF Impact Tracker has been set up to offer support for upcoming negotiations on the potential adoption of the IMO
            Net-Zero Framework to reduce emissions from global shipping. Publicly available on the UCL Shipping and Oceans Research 
            Group’s website, the ‘NZF Economic Impacts Tracker’ empowers delegations with key data that can be used to compare
            trade-offs across four key policy options currently under consideration. 
            
            The tool offers detailed statistical data for many countries not well-represented within previous impact assessment 
            processes, including Least Developed Countries, Small-Island Developing States and other particularly exposed economies 
            for which only regionally aggregated results have previously been available. Building upon methods developed during the
            IMO-led Comprehensive Impact Assessment process, the supporting methodology combines bespoke trade statistics with 
            international vessel voyage data to estimate NZF economic impacts at a granular level across thousands of individual 
            trade flows on the importer and exporter side.   
            
             The results, made publicly available via the dashboard, enable users to better understand likely maritime transport cost 
            and price changes to mercantile commodity flows for a given country of interest. Crucially, the tool offers users the 
            chance to gauge how NZF impacts can be expected to manifest on food security-relevant commodities, as well as how aggregate
            NZF-induced impacts compare against the costs of climate change expected to 2050.
            """)

st.subheader("Country Selection", divider="grey")

st.write(
    f"Currently selected country: **{st.session_state.iso_country}**"
)

st.write(
    "Use the country selector in the sidebar to switch between "
    "countries. Your selection will apply across all pages "
    "of the dashboard."
)

st.divider()

# from country_selector import country_selector

# country_selector()


st.subheader('The Global Picture')
st.divider()

#Segmented controls

trade_flow = st.segmented_control(
    "Which Trade flow are you interested in?",
    options=["Import", "Export"],
    default="Import",
    key="trade_flow"
)

cost_measure = st.segmented_control(
    "What measure of cost relative to a BAU scenario are you interested in?",
    options=[
        "CIF/FOB price of Imports/Exports",
       # "Maritime Logistics Cost",
        "Maritime Transport Cost",
        "MTC as % of GDP"
    ],
    default="CIF/FOB price of Imports/Exports",
    key="cost_measure"
)

scenario = st.segmented_control(
    "Which Scenario would you like to view?",
    options=[
        "NZF as-is",
        "Levy",
        "Brazil",
        "LISCR",
     #   "Direct"
    ],
    default="NZF as-is",
    key="scenario"
)


#Match selections to datasets

dataset_map = {

    "Import": {
        "Maritime Transport Cost":
            "impact_im_costs_to_bau_pct_bau_v0.64_combined.csv",

        # "Maritime Logistics Cost":
        #     "impact_im_costs_to_bau_pct_ciffob_v0.64_combined.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_im_costs_to_bau_pct_cif_v0.64_combined.csv",

        "MTC as % of GDP":
            "impact_im_costs_to_bau_pct_gdp_v0.64_combined.csv"
    },

    "Export": {
        "Maritime Transport Cost":
            "impact_ex_costs_to_bau_pct_bau_v0.64_combined.csv",

        # "Maritime Logistics Cost":
        #     "impact_ex_costs_to_bau_pct_ciffob_v0.64_combined.csv",

        "CIF/FOB price of Imports/Exports":
            "impact_ex_costs_to_bau_pct_fob_v0.64_combined.csv",

        "MTC as % of GDP":
            "impact_ex_costs_to_bau_pct_gdp_v0.64_combined.csv"
    }
}

selected_file = dataset_map[trade_flow][cost_measure]


#Load selected dataset


base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/datasets/"
)

@st.cache_data
def load_data(filename):

    df = pd.read_csv(base_url + filename)

    return df


df = load_data(selected_file)


#Melt dataset from wide to long

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

#Standardise scenario names

df_long["Scenario"] = (
    df_long["Scenario"]
    .astype(str)
    .str.strip()
    .str.strip("'\"")
)

df_long["Scenario"] = df_long["Scenario"].replace({
    "as-is": "NZF as-is"
})

#Filter selected scenario

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


#Set fixed colour scale across all years

all_values = df_long["Value"].dropna()

min_value = min(0, all_values.min())
max_value = max(0, all_values.max())

if max_value <= min_value:
    max_value = min_value + 1


#Create animated choropleth map

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

    #projection="natural earth",

    title=f"{trade_flow} - {cost_measure} - {scenario}"
)


fig.update_geos(
    #fitbounds="locations",
    visible=False,
    showcountries=True,
    center=dict(lat=0,lon=0),
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


#Animation controls


if fig.layout.updatemenus:

    fig.layout.updatemenus[0].buttons[0].args[1][
        "frame"
    ]["duration"] = 900

    fig.layout.updatemenus[0].buttons[0].args[1][
        "transition"
    ]["duration"] = 300


#Display map


st.plotly_chart(
    fig,
    width='stretch',
    config={"displayModeBar": True}
)




# ---------------------------------------------------------
# Global cumulative GHG emissions
# ---------------------------------------------------------

import plotly.graph_objects as go

st.subheader("Global Cumulative GHG Emissions", divider="grey")


# Segmented control

emissions_measure = st.segmented_control(
    "Which GHG emissions measure are you interested in?",
    options=[
        "Absolute GHG Emissions",
        "GHG Emissions Reduction Relative to BAU"
    ],
    default="Absolute GHG Emissions",
    key="global_emissions_measure"
)


# Load dataset

@st.cache_data
def load_cumulative_emissions():

    url = (
        "https://raw.githubusercontent.com/"
        "UCL-ShippingGroup/Impact-Tracker/main/datasets/"
        "cumulative_emissions_v9_round_2.csv"
    )

    return pd.read_csv(url)


df_emissions = load_cumulative_emissions()


# Define scenario columns and display names

scenario_columns = {
    "Brazil NZF softer start, harder finish_biofuel_ramp_up_2035": "Brazil",
    "LISCR concept_biofuel_ramp_up_2035": "LISCR",
    "NZF 'as is'_biofuel_ramp_up_2035": "NZF 'as is'",
    "No IMO policy_biofuel_ramp_up_2035": "BAU",
    "Tuvalu levy_biofuel_ramp_up_2035": "Levy"
}


# Convert columns to numeric

df_emissions["estimation_year"] = pd.to_numeric(
    df_emissions["estimation_year"],
    errors="coerce"
)

for column in scenario_columns:
    df_emissions[column] = pd.to_numeric(
        df_emissions[column],
        errors="coerce"
    )

df_emissions = df_emissions.sort_values("estimation_year")


# Define BAU column

bau_column = "No IMO policy_biofuel_ramp_up_2035"


# Create line chart

fig_emissions = go.Figure()

for column, scenario in scenario_columns.items():

    # For reduction chart, exclude BAU
    if (
        emissions_measure == "GHG Emissions Reduction Relative to BAU"
        and column == bau_column
    ):
        continue

    # Select values depending on measure
    if emissions_measure == "Absolute GHG Emissions":

        values = df_emissions[column]

    else:

        values = (
            df_emissions[column]
            - df_emissions[bau_column]
        )

    fig_emissions.add_trace(
        go.Scatter(
            x=df_emissions["estimation_year"],
            y=values,

            mode="lines+markers",
            name=scenario,

            line=dict(width=2.5),
            marker=dict(size=5),

            hovertemplate=(
                "<b>" + scenario + "</b><br>"
                "Year: %{x:.0f}<br>"
                + (
                    "Cumulative: %{y:,.2f} million tonne CO2e"
                    if emissions_measure == "Absolute GHG Emissions"
                    else "Reduction: %{y:,.2f} million tonne CO2e"
                )
                + "<extra></extra>"
            )
        )
    )


# Set Y-axis title

if emissions_measure == "Absolute GHG Emissions":

    yaxis_title = "Cumulative (million tonne CO2e)"

else:

    yaxis_title = (
        "Cumulative Reduction Relative to BAU "
        "(million tonne CO2e)"
    )


# Format chart

fig_emissions.update_layout(

    height=600,
    template="plotly_white",

    hovermode="closest",

    xaxis=dict(
        title="Year",
        tickformat="d",
        dtick=2
    ),

    yaxis=dict(
        title=yaxis_title,
        tickformat=",.0f",
        zeroline=True,
        zerolinecolor="lightgrey"
    ),

    legend=dict(
        title=None,
        orientation="h",
        yanchor="top",
        y=-0.18,
        xanchor="center",
        x=0.5
    ),

    margin=dict(
        l=90,
        r=30,
        t=30,
        b=110
    ),

    paper_bgcolor="rgba(0,0,0,0)"
)


# Display chart

st.plotly_chart(
    fig_emissions,
    width="stretch",
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


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


#Get selected country from home page


selected_country = st.session_state.get(
    "iso_country",
    None
)

selected_iso3 = st.session_state.get(
    "iso_3",
    None
)

if selected_country is None or selected_iso3 is None:
    st.warning("Please select a country on the home page.")
    st.stop()

selected_iso3 = str(selected_iso3).strip().upper()


#Section title


st.subheader(
    "{0} in the Global Context".format(selected_country),
    divider="grey"
)


#Metric selector

metric_global = st.segmented_control(
    "What measure of cost relative to a BAU scenario are you interested in?",
    options=[
        "Maritime Transport Cost",
        "Maritime Logistics Cost",
        "CIF/FOB price of Imports/Exports",
        "MTC as % of GDP"
    ],
    default="Maritime Transport Cost",
    key="metric_global_context"
)


years = [
    2029, 2032, 2035, 2038,
    2041, 2044, 2047, 2050
]

selected_year = st.select_slider(
    "Year",
    options=years,
    value=2050,
    key="global_context_year"
)


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
            "impact_ex_costs_to_bau_pct_fob_v0.64_combined.csv",

        "MTC as % of GDP":
            "impact_ex_costs_to_bau_pct_gdp_v0.64_combined.csv"
    }
}

#Load and melt datasets


base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/datasets/"
)

@st.cache_data
def load_global_context_data(filename):

    df = pd.read_csv(base_url + filename)

    year_cols = [
        "2029", "2032", "2035", "2038",
        "2041", "2044", "2047", "2050"
    ]

    # Melt from wide to long
    df = df.melt(
        id_vars=["Country", "alpha-3", "Scenario"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value"
    )

    # Convert data types
    df["Year"] = df["Year"].astype(int)

    df["Value"] = pd.to_numeric(
        df["Value"],
        errors="coerce"
    )

    df["alpha-3"] = (
        df["alpha-3"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Standardise scenario names
    df["Scenario"] = (
        df["Scenario"]
        .astype(str)
        .str.strip()
        .str.strip("'\"")
    )

    df["Scenario"] = df["Scenario"].replace({
        "as-is": "NZF"
    })

    return df


# Load imports and exports
imports_df = load_global_context_data(
    dataset_map["Import"][metric_global]
)

exports_df = load_global_context_data(
    dataset_map["Export"][metric_global]
)


#Filter selected year

imports_df = imports_df[
    imports_df["Year"] == selected_year
].copy()

exports_df = exports_df[
    exports_df["Year"] == selected_year
].copy()

# Remove missing observations
imports_df = imports_df.dropna(
    subset=["Value"]
)

exports_df = exports_df.dropna(
    subset=["Value"]
)


# Define scenarios


scenarios = [
    "NZF",
    "Levy",
    "Brazil",
    "LISCR",
    "Direct"
]


#Function to create swarm and box plot


def create_global_context_plot(data, selected_iso3):

    fig = go.Figure()

    # Loop through each scenario
    for i, scenario in enumerate(scenarios):

        subset = data[
            data["Scenario"] == scenario
        ].copy()

        if subset.empty:
            continue

        position = i

       
        # Box plot
        

        values = subset["Value"].dropna()

        mean_value = values.mean()
        median_value = values.median()
        q1_value = values.quantile(0.25)
        q3_value = values.quantile(0.75)
        min_value = values.min()
        max_value = values.max()

        fig.add_trace(
            go.Box(
                x=[position] * len(values),
                y=values,

                name=scenario,

                boxpoints=False,
                width=0.5,
                showlegend=False,

                # Display mean on the box
                boxmean=True,

                hovertemplate=(
                    "<b>" + scenario + "</b><br>"
                    + f"Maximum: {max_value:.2f}%<br>"
                    + f"Q3 (75%): {q3_value:.2f}%<br>"
                    + f"Median: {median_value:.2f}%<br>"
                    + f"Mean: {mean_value:.2f}%<br>"
                    + f"Q1 (25%): {q1_value:.2f}%<br>"
                    + f"Minimum: {min_value:.2f}%<br>"
                    + f"Countries: {len(values)}"
                    + "<extra></extra>"
                ),

                line=dict(
                    color="rgba(80,80,80,0.8)",
                    width=1.5
                ),

                fillcolor="rgba(180,180,180,0.25)"
            )
        )

       

        rng = np.random.default_rng(42 + i)

        jitter = rng.uniform(
            -0.15,
            0.15,
            size=len(subset)
        )

        x_values = position + jitter

        is_selected = (
            subset["alpha-3"] == selected_iso3
        )


        normal = subset[~is_selected]

        normal_x = x_values[~is_selected.to_numpy()]

        if len(normal) > 0:

            fig.add_trace(
                go.Scatter(
                    x=normal_x,
                    y=normal["Value"],

                    mode="markers",

                    showlegend=False,

                    marker=dict(
                        size=7,
                        color="blue",
                        opacity=0.65
                    ),

                    customdata=normal[
                        ["Country", "alpha-3"]
                    ].to_numpy(),

                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "ISO: %{customdata[1]}<br>"
                        + scenario + "<br>"
                        "Change: %{y:.2f}%"
                        "<extra></extra>"
                    )
                )
            )

        selected = subset[is_selected]

        selected_x = x_values[
            is_selected.to_numpy()
        ]

        if len(selected) > 0:

            fig.add_trace(
                go.Scatter(
                    x=selected_x,
                    y=selected["Value"],

                    mode="markers",

                    showlegend=False,

                    marker=dict(
                        size=14,
                        color="yellow",

                        line=dict(
                            color="black",
                            width=1.5
                        )
                    ),

                    customdata=selected[
                        ["Country", "alpha-3"]
                    ].to_numpy(),

                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "ISO: %{customdata[1]}<br>"
                        + scenario + "<br>"
                        "Change: %{y:.2f}%"
                        "<extra></extra>"
                    )
                )
            )

    
    #Legend for country dots
  

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name="Other countries",

            marker=dict(
                size=7,
                color="blue",
                opacity=0.65
            ),

            hoverinfo="skip"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name="Selected country",

            marker=dict(
                size=14,
                color="yellow",

                line=dict(
                    color="black",
                    width=1.5
                )
            ),

            hoverinfo="skip"
        )
    )

    
    fig.update_layout(

        height=600,

        template="plotly_white",

        hovermode="closest",
        hoverdistance=5,

        margin=dict(
            l=65,
            r=20,
            t=40,
            b=85
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),

        xaxis=dict(
            tickmode="array",

            tickvals=[
                0, 1, 2, 3, 4
            ],

            ticktext=scenarios,

            range=[
                -0.5,
                4.5
            ],

            title=None
        ),

        yaxis=dict(
            title="Change relative to BAU (%)",
            ticksuffix="%",

            zeroline=True,
            zerolinecolor="lightgrey"
        ),

        boxmode="overlay"
    )

    return fig


#Display imports and exports side by side


col1, col2 = st.columns(2)

with col1:

    st.markdown("#### Imports")

    imports_fig = create_global_context_plot(
        imports_df,
        selected_iso3
    )

    st.plotly_chart(
        imports_fig,
        width='stretch',
        key="global_context_imports"
    )


with col2:

    st.markdown("#### Exports")

    exports_fig = create_global_context_plot(
        exports_df,
        selected_iso3
    )

    st.plotly_chart(
        exports_fig,
        width='stretch',
        key="global_context_exports"
    )


# Check whether selected country has data


if not (
    (imports_df["alpha-3"] == selected_iso3).any()
    or
    (exports_df["alpha-3"] == selected_iso3).any()
):
    st.info(
        f"No observations for {selected_country} "
        "in the selected datasets. "
        "The charts show available countries."
    )

st.markdown(
    """
    ##### Disclaimer

    The content on this website is for informational and educational
    purposes only. It should not be considered as financial,
    investment, or legal advice. We are not financial advisors,
    and the information provided is not a substitute for
    professional advice from a qualified expert who is aware
    of your individual circumstances. Always conduct your own
    research and consult with a licensed financial professional
    before making any investment or financial decisions.
    Any reliance you place on the information provided on this
    site is strictly at your own risk. We are not liable for any
    losses or damages incurred from the use of this information.
    """
)
