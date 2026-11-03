import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import time
from urllib.parse import quote
input_dir = "https://raw.githubusercontent.com/james-stewart-808/inventory-tracker/main/datasets/"

def download_as_csv(file, label, filename):
    return st.download_button(
            data=file.to_csv(index=False),
            label=label,
            file_name=filename)

st.sidebar.markdown(
    "Costs of Climate Change data sourced from Kahn et al. (2021) and Mohaddes and Raissi (2024)."
)

st.subheader(
    "Impact of Maritime Transport Costs on GDP",
    divider="grey"
)

st.caption(
    "Change in Maritime Transport Costs as a percentage of GDP "
    "relative to the Business as Usual (BAU) scenario."
)

# Import / Export segmented control
trade_choice = st.segmented_control(
    "Trade Flow",
    options=["Import", "Export"],
    default="Import"
)

# Select dataset
if trade_choice == "Import":
    filename = "impact_im_costs_to_bau_pct_gdp_v0.64.csv"
else:
    filename = "impact_ex_costs_to_bau_pct_gdp_v0.64.csv"

# Load selected country's dataset
country = st.session_state.iso_country

url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/"
    f"impact/{quote(country, safe='')}/{filename}"
)

df_mtc = pd.read_csv(url)

# Rename As-is scenario
df_mtc["Scenario"] = df_mtc["Scenario"].replace(
    {"as-is": "NZF as-is"}
)

# Identify year columns
year_cols = [
    col for col in df_mtc.columns
    if str(col).isdigit()
]

# Reshape from wide to long
df_mtc_long = df_mtc.melt(
    id_vars=["Scenario"],
    value_vars=year_cols,
    var_name="year",
    value_name="MTC"
)

# Convert columns to numeric
df_mtc_long["year"] = df_mtc_long["year"].astype(int)

df_mtc_long["MTC"] = pd.to_numeric(
    df_mtc_long["MTC"],
    errors="coerce"
)

df_mtc_long = df_mtc_long.dropna(subset=["MTC"])

# Sort by year
df_mtc_long = df_mtc_long.sort_values("year")

# Create line chart
fig_mtc = px.line(
    df_mtc_long,
    x="year",
    y="MTC",
    color="Scenario",
    markers=True,
    labels={
        "year": "Year",
        "MTC": "Change in Maritime Transport Costs (% of GDP)",
        "Scenario": "Scenario"
    }
)

# Hover formatting
fig_mtc.update_traces(
    hovertemplate=(
        "Year: %{x}<br>"
        "Change: %{y:.4f}%"
        "<extra>%{fullData.name}</extra>"
    )
)

# Chart layout
fig_mtc.update_layout(
    xaxis_title="Year",
    yaxis_title="Change in Maritime Transport Costs (% of GDP)",
    hovermode="x unified",
    legend_title="Scenario",
    height=500,
    margin=dict(l=20, r=20, t=30, b=20)
)

fig_mtc.update_xaxes(
    showgrid=True,
    tickmode="array",
    tickvals=sorted(df_mtc_long["year"].unique())
)

fig_mtc.update_yaxes(
    showgrid=True,
    ticksuffix="%"
)

st.plotly_chart(
    fig_mtc,
    width="stretch"
)
##### COSTS OF CLIMATE CHANGE ######
st.set_page_config(layout='wide')
st.title('National Macroeconomic Effects of Climate Scenarios')

st.markdown(
    """
    Using data from Kahn et al. (2021) and Mohaddes and Raissi (2024) we are able to show country-specific annual GDP per-capita losses from global warming \
    using the most recent climate scenarios of the Intergovernmental Panel on Climate Change (IPCC). We have chosen this study for its thorough scope, covering 174 \
    countries and numerous SSP and RCP scenario combinations that range from optimistic to pessimistic as follows:
    
    - SSP1-2.6: A scenario consistent with Paris Agreement pledges projecting a sustainable future where global \
                warming is limited to below 2°C and between 1.5-1.8°C above the pre industrial average by 2100.  
    - SSP2-4.5: A 'middle of the road' scenario that most closely aligns with 1960-2014 trends where a 'business as usual' approach leads to around 2.7°C of warming.  
    - SSP3-7.0: A more pessimistic scenario reflecting policy reversals, low international cooperation and high material intensive consumption that leads to 3.6°C of warming.  
    - SSP5-8.5: A high emissions scenario where with intensive fossil fuel expansion and minimal climate mitigation. This is deemed unrealistic now but included to show a worst case scenario. 
             
    Furthermore, previous literature has projected the impact of increasing temperatures on GDP by using a counterfactual scenario where there \
    is 'no further warming'. The problem with this is that there are no realistic pathways to a scenario in which baseline temperatures would remain constant \
    leading to overstated loss predictions. Therefore, a more realistic counterfactual is proposed where temeprature in each country rises according to its trend \ 
    from 1960-2014. To calculate GDP losses in simple terms, a 30-year moving average temperature is used to represent the speed at which historical norms change, i.e how quickly \ 
    countries adapt to rising temperatures. This moving average is subtracted from the projected temperature for a given year to produce a gap. The same process is \ 
    carried out for the counterfactual world, where temperatures rise only at their modest historical pace, producing its own gap. \
    The counterfactual gap is then subtracted from the scenario gap, and it is this resulting temperature disparity, representing the extra warming that economies have not \ 
    yet adapted to, above and beyond what would have occurred anyway, that drives the estimated GDP losses. 
    Below, you can find data for your selected country, compare countries, and view the global picture through to 2100.
    """
)  

df_profile = 'gdp_change'

df_1 = pd.read_csv("https://raw.githubusercontent.com//UCL-ShippingGroup/Impact-Tracker/main/gdp/{0}/{1}.csv".format(st.session_state.iso_country, df_profile))


filtered_df1 = df_1[df_1['year'].isin([2030,2040,2050,2060,2070,2080,2090,2100])]

df_world = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/Impact-Tracker/main/datasets/world_gdp_change.csv")

st.subheader("Country and Global GDP per Capita Losses", divider='grey')
#st.markdown("##### Country and Global GDP per Capita Losses")
st.caption("Global GDP losses are calculated by averaging the losses across countries using PPP-GDP weights")

# First segmented control
chart_choice = st.segmented_control(
    label="Would you like to view your country or global GDP losses?",
    options=["Country", "World"],
    default="Country"
)

# Second segmented control
chart_type = st.segmented_control(
    label="Select chart type",
    options=["Bar", "Line"],
    default="Bar"
)

# COUNTRY CHARTS
if chart_choice == "Country":

    # Grouped bar chart (filtered data)
    if chart_type == "Bar":
        fig = px.bar(
            filtered_df1,
            x='year',
            y='gdp_per_c',
            color='Scenario',
            barmode='group'
        )

    # Line chart (full data)
    else:
        fig = px.line(
            df_1,
            x='year',
            y='gdp_per_c',
            color='Scenario',
            markers=True
        )

# WORLD CHARTS
else:

    # Grouped bar chart
    if chart_type == "Bar":
        fig = px.bar(
            df_world,
            x='Year',
            y='gdp_change',
            color='Scenario',
            barmode='group'
        )

    # Line chart
    else:
        fig = px.line(
            df_world,
            x='Year',
            y='gdp_change',
            color='Scenario',
            markers=True
        )

# Common formatting
fig.update_xaxes(showgrid=True)

# Display chart
st.plotly_chart(fig, width='stretch')      
#width='content'

st.subheader("Country Comparison", divider = 'grey')
#st.markdown("##### Country Comparison")
st.caption("Select countries you wish to compare. To zoom into specific time scales, create a box over the desired area and the graph will automatically zoom in") 

df_2 = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/Impact-Tracker/main/datasets/country_gdp.csv")
ssp_1 = df_2[df_2['Scenario'] == 'SSP1-2.6']
ssp_2 = df_2[df_2['Scenario'] == 'SSP2-4.5']  
ssp_3 = df_2[df_2['Scenario'] == 'SSP3-7.0']  
ssp_5 = df_2[df_2['Scenario'] == 'SSP5-8.5']  

comparison_countries = st.multiselect(
    "Select Countries",
    options=sorted(df_2['country'].unique()),
    default=[st.session_state.iso_country]
)
selected_data = df_2[
    df_2['country'].isin(comparison_countries)
]

max_abs = max(
    abs(selected_data['gdp_per_c'].min()),
    abs(selected_data['gdp_per_c'].max())
)

def make_scenario_chart(data, scenario):

    filtered = data[
        (data['country'].isin(comparison_countries)) &
        (data['Scenario'] == scenario)
    ]

    fig = px.line(
        filtered,
        x='year',
        y='gdp_per_c',
        color='country',
        #markers=True,
        title=scenario
    )

    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title='Country'
    )

    fig.update_yaxes(
        title='% GDP change',
        ticksuffix='%',
        dtick=2,
        range=[-max_abs, max_abs]
    )

    return fig

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        make_scenario_chart(df_2, 'SSP1-2.6'),
        width='stretch'
    )

with col2:
    st.plotly_chart(
        make_scenario_chart(df_2, 'SSP2-4.5'),
        width='stretch'
    )

col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(
        make_scenario_chart(df_2, 'SSP3-7.0'),
        width='stretch'
    )

with col4:
    st.plotly_chart(
        make_scenario_chart(df_2, 'SSP5-8.5'),
        width='stretch'
    )

st.subheader("Global GDP Losses for Each Scenario",divider = 'grey')
#st.markdown("##### "Global GDP Losses for Each Scenario")
st.caption("Current trajectories of global temperature increases range from 2.1-2.8°C with implementation of the latest nationally determined contributions. \
Current policies are not consistent with these policies placing predicted warming at the upper bound of this range. This is consistent with SSP2-4.5 and closing towards \
SSP3-7.0. This tool shows the global importance of continued international cooperation and the avoidance of policy \
reversals.")

options = ['SSP1-2.6','SSP2-4.5','SSP3-7.0','SSP5-8.5']
ssp_selection = st.segmented_control(
           "Which scenario would you like to explore", 
           options,
           default = 'SSP1-2.6')

ssp = df_2[df_2['Scenario'] == ssp_selection]

ssp = ssp[ssp['year'] % 5 == 0]

fig_2 = px.choropleth(ssp, locations="iso",
                    color='gdp_per_c',
                    hover_name="country",
                    hover_data={'year': True,'gdp_per_c': ':.2f'},
                    #locationmode="country names",
                    animation_frame='year',
                    range_color = [-9.5,9.5],
                    #color_continuous_midpoint = 0,
                    color_continuous_scale=px.colors.diverging.RdYlGn)
fig_2.update_layout(paper_bgcolor="white",title_text = 'Annual GDP Per Capita % Change',height= 600, width=400,font_size=18)
fig_2.update_geos(
    showcoastlines=True,
    coastlinecolor="Black",
    showland=True,
    showcountries=True,
    countrycolor="gray",
    fitbounds="locations"
)
st.plotly_chart(fig_2,width='stretch')
#margin=dict(l=20,r=0,b=0,t=70,pad=0)
#height= 700

#width='stretch'        

st.markdown("##### References")

st.write(
"""
Kahn et al. (2021). Long-term macroeconomic effects of climate change: A cross-country analysis.\n
Mohaddes and Raissi. (2024). Rising Temperatures, Melting Incomes: Country-Specific Macroeconomic Effects of Climate Scenarios. 
"""
)
