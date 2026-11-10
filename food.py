import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

from country_selector import country_selector

country_selector()

# ---------------------------------------------------------
# 1. Page title and selected country
# ---------------------------------------------------------

st.title("Food Security")

st.write(
    """
    The Food Security page provides a detailed assessment of the potential economic impacts of different NZF scenarios on a country's seaborne food imports.
    By examining changes in maritime transport costs across different food groups, the analysis highlights how the composition of a country's food import portfolio may influence its exposure to NZF-related cost increases.
    The first chart illustrates the evolution of total food import costs across different NZF scenarios. Users can examine these impacts through the same measures used in the impact page. The second chart provides a more detailed 
    breakdown of these impacts by food group, 
    allowing users to compare how different categories of food imports respond to alternative NZF scenarios. This helps identify food groups that may be particularly exposed to changes 
    in maritime transport costs and highlights differences in the distribution of potential economic impacts across the food import portfolio.
    
    The Food Import Composition charts examine the proportion of total food import value and weight attributable to each food group. Comparing these measures provides insight into the structure of 
    a country's food imports, particularly where certain food groups account for a disproportionately large share of physical import weight relative to their economic value. 
   
    Finally, the Food Group Contributions chart examines how individual food groups contribute to the overall percentage change in food import CIF costs relative to BAU. Each 
    group's contribution is calculated by weighting its percentage change in CIF costs by its share of total food import value. This allows users to distinguish between food 
    groups experiencing the largest relative cost increases and those contributing most significantly to the overall economic impact.
    By hovering over individual segments, users can examine each food group's percentage change in CIF costs, its proportion of total food import value, and 
    its weighted contribution to the overall change. This enables direct comparisons between the economic importance of different food groups and their contribution to changes in overall food import costs.
    Together, these visualisations provide insight into the potential economic pressures that alternative NZF scenarios may place on food imports, particularly for countries with a 
    high dependence on seaborne trade. While changes in import costs do not directly measure food security outcomes, they can help identify potential vulnerabilities within national food import portfolios.
    Further information on the methodology, food group classifications and calculation of economic impacts is available in the Technical Annex.

selected_country = st.session_state.get("iso_country", None)

if selected_country is None:
    st.warning("Please select a country on the Home page.")
    st.stop()

st.subheader(f"Food Security Impact: {selected_country}")

# ---------------------------------------------------------
# 2. Select measure
# ---------------------------------------------------------

measure = st.segmented_control(
    "What measure of cost are you Interested in?",
    options=[
        "CIF Price of Imports Relative to BAU",
        "MTC"
    ],
    default="CIF Price of Imports Relative to BAU",
    key="food_impact_measure"
)


# ---------------------------------------------------------
# 3. Load selected country's datasets
# ---------------------------------------------------------

base_url = (
    "https://raw.githubusercontent.com/"
    "UCL-ShippingGroup/Impact-Tracker/main/food/"
)

# Get selected country's ISO code
selected_iso_code = st.session_state.iso_code

# Ensure ISO code is three digits
selected_iso_code = str(selected_iso_code).zfill(3)

# Construct folder name: 008 - Albania
folder_name = f"{selected_iso_code} - {selected_country.strip()}"

# URL encode folder name
country_url = quote(folder_name, safe="")


@st.cache_data
def load_food_data(country):

    country_path = base_url + country + "/"

    # Load MTC dataset
    df_mtc = pd.read_csv(
        country_path + "food_total_costs_usd_tot_v0.03.csv"
    )

    # Load CIF dataset
    df_cif = pd.read_csv(
        country_path + "food_total_costs_pct_cif_tot_v0.03.csv"
    )

    return df_mtc, df_cif


# Load datasets for selected country
try:
    df_mtc, df_cif = load_food_data(country_url)

except Exception as e:
    st.error(
        f"Unable to load food data for {selected_country}."
    )
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
   # "direct": "Direct"
}

#All scednarios except Direct
df_long = df_long[
    df_long["Scenario"].str.lower() != "direct"
].copy()

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
# 9. Select measure
# ---------------------------------------------------------

measure_food = st.segmented_control(
    "What measure of cost are you Interested in?",
    options=[
        "CIF Price of Imports Relative to BAU",
        "MTC"
    ],
    default="CIF Price of Imports Relative to BAU",
    key="food_group_measure"
)


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
    chart_title_food = "Food Import MTC by Scenario"

else:

    df_food = df_cif_food.copy()
    y_axis_title_food = "CIF Price of Imports Relative to BAU (%)"
    chart_title_food = "Food Import CIF Price Change by Scenario"


# ---------------------------------------------------------
# 12. Exclude total row
# ---------------------------------------------------------

df_food = df_food[
    df_food["food_group"].astype(str).str.strip().str.lower()
    != "total"
].copy()

df_food["food_group"] = (
    df_food["food_group"]
    .astype(str)
    .str.strip()
)


# ---------------------------------------------------------
# 13. Select food group
# ---------------------------------------------------------

food_group_options = sorted(
    df_food["food_group"].dropna().unique().tolist()
)

if not food_group_options:
    st.warning("No food groups available.")
    st.stop()

selected_food_group = st.segmented_control(
    "Which Food Group are you interested in?",
    options=food_group_options,
    default=food_group_options[0],
    key="food_group_selection"
)


# ---------------------------------------------------------
# 14. Filter selected food group and reshape data
# ---------------------------------------------------------

df_food = df_food[
    df_food["food_group"] == selected_food_group
].copy()

# Identify scenario/year columns
scenario_cols_food = df_food.columns[
    df_food.columns.str.match(r"^[A-Za-z0-9]+_\d{2,4}$")
].tolist()

if not scenario_cols_food:
    st.warning("No scenario/year columns found.")
    st.stop()

# Reshape from wide to long
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

# Scenario names
scenario_names = {
    "bau": "BAU",
    "levy": "Levy",
    "asis": "NZF as-is",
    "brazil": "Brazil",
    "liscr": "LISCR",
 #   "direct": "Direct"
}

df_food_long["Scenario"] = (
    df_food_long["Scenario"]
    .str.lower()
    .map(scenario_names)
)

# Ensure numeric values
df_food_long["Value"] = pd.to_numeric(
    df_food_long["Value"],
    errors="coerce"
)

df_food_long = df_food_long.dropna(
    subset=["Scenario", "Value"]
)

# Set scenario order
scenario_order = [
    "BAU",
    "NZF as-is",
    "Levy",
    "Brazil",
    "LISCR",
 #   "Direct"
]

df_food_long = df_food_long.sort_values(
    ["Scenario", "year"]
)


# ---------------------------------------------------------
# 15. Create Plotly line chart
# ---------------------------------------------------------

fig_food = px.line(
    df_food_long,
    x="year",
    y="Value",
    color="Scenario",
    markers=True,
    title=f"{chart_title_food}: {selected_food_group}",
    category_orders={
        "Scenario": scenario_order
    },
    labels={
        "year": "Year",
        "Value": y_axis_title_food,
        "Scenario": "Scenario"
    }
)

# Format hover
fig_food.update_traces(
    marker=dict(size=9),
    line=dict(width=2.5),
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Year: %{x}<br>"
        + y_axis_title_food + ": %{y:,.2f}"
        + "<extra></extra>"
    )
)

fig_food.update_layout(
    xaxis_title="Year",
    yaxis_title=y_axis_title_food,
    hovermode="closest",
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
        b=110
    )
)

fig_food.update_xaxes(
    tickmode="array",
    tickvals=sorted(df_food_long["year"].unique())
)

fig_food.update_yaxes(
    tickformat=",.2f"
)

st.plotly_chart(
    fig_food,
    use_container_width=True
)
# ---------------------------------------------------------
# 16. Food Import Composition
# ---------------------------------------------------------

st.subheader("Food Import Composition")


# ---------------------------------------------------------
# 17. Load selected country's dataset
# ---------------------------------------------------------

@st.cache_data
def load_food_composition_data(country):

    country_path = base_url + country + "/"

    df_composition = pd.read_csv(
        country_path + "food_total_usd_tot_v0.03.csv"
    )

    return df_composition


try:
    df_composition = load_food_composition_data(
        country_url
    )

except Exception as e:
    st.error(
        f"Unable to load food composition data for {selected_country}."
    )
    st.exception(e)
    st.stop()


# ---------------------------------------------------------
# 18. Prepare data
# ---------------------------------------------------------

# Exclude total row if present
df_composition = df_composition[
    df_composition["food_group"].astype(str).str.strip().str.lower()
    != "total"
].copy()

# Ensure percentage columns are numeric
df_composition["pct_val_food"] = pd.to_numeric(
    df_composition["pct_val_food"],
    errors="coerce"
)

df_composition["pct_vol_food"] = pd.to_numeric(
    df_composition["pct_vol_food"],
    errors="coerce"
)


# ---------------------------------------------------------
# 19. Create side-by-side pie charts
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.markdown("#### Proportion of Food Import Value")

    fig_val = px.pie(
        df_composition,
        names="food_group",
        values="pct_val_food",
        color="food_group"
    )

    fig_val.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "%{label}<br>"
            "Percentage: %{value:.2f}%"
            "<extra></extra>"
        )
    )

    fig_val.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=90
        )
    )

    st.plotly_chart(
        fig_val,
        use_container_width=True
    )


with col2:

    st.markdown("#### Proportion of Food Import Weight")

    fig_vol = px.pie(
        df_composition,
        names="food_group",
        values="pct_vol_food",
        color="food_group"
    )

    fig_vol.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "%{label}<br>"
            "Percentage: %{value:.2f}%"
            "<extra></extra>"
        )
    )

    fig_vol.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=90
        )
    )

    st.plotly_chart(
        fig_vol,
        use_container_width=True
    )


import plotly.graph_objects as go

# ---------------------------------------------------------
# 20. Diverging stacked bar chart
# ---------------------------------------------------------

st.subheader("Food Group Contributions to CIF Changes")

st.caption(
    "Contribution of each food group to the overall percentage "
    "change in food import CIF costs relative to BAU, weighted "
    "by its proportion of total import value."
)


# ---------------------------------------------------------
# 21. Load selected country's data
# ---------------------------------------------------------

@st.cache_data
def load_food_contribution_data(country):

    country_path = base_url + country + "/"

    df_share = pd.read_csv(
        country_path + "food_total_usd_tot_v0.03.csv"
    )

    df_change = pd.read_csv(
        country_path + "food_total_costs_pct_cif_v0.03.csv"
    )

    return df_share, df_change


try:
    df_share, df_change = load_food_contribution_data(
        country_url
    )

except Exception as e:
    st.error(
        f"Unable to load food contribution data for {selected_country}."
    )
    st.exception(e)
    st.stop()


# ---------------------------------------------------------
# 22. Prepare food group shares
# ---------------------------------------------------------

df_share = df_share[
    df_share["food_group"].astype(str).str.strip().str.lower()
    != "total"
].copy()

df_share["food_group"] = (
    df_share["food_group"].astype(str).str.strip()
)

df_share["pct_val_food"] = pd.to_numeric(
    df_share["pct_val_food"],
    errors="coerce"
)

# Convert shares from percentages to proportions
df_share["Share"] = df_share["pct_val_food"] / 100


# ---------------------------------------------------------
# 23. Prepare CIF percentage change data
# ---------------------------------------------------------

df_change = df_change[
    df_change["food_group"].astype(str).str.strip().str.lower()
    != "total"
].copy()

df_change["food_group"] = (
    df_change["food_group"].astype(str).str.strip()
)

scenario_cols = df_change.columns[
    df_change.columns.str.match(
        r"^[A-Za-z0-9]+_\d{2,4}$"
    )
].tolist()

df_change_long = df_change.melt(
    id_vars=["food_group"],
    value_vars=scenario_cols,
    var_name="Scenario_Year",
    value_name="CIF_Change"
)

# Extract scenario and year
df_change_long[["Scenario", "year"]] = (
    df_change_long["Scenario_Year"].str.rsplit(
        "_", n=1, expand=True
    )
)

df_change_long["year"] = (
    df_change_long["year"].astype(int)
)

df_change_long["year"] = df_change_long["year"].apply(
    lambda x: x + 2000 if x < 100 else x
)

df_change_long["CIF_Change"] = pd.to_numeric(
    df_change_long["CIF_Change"],
    errors="coerce"
)


# ---------------------------------------------------------
# 24. Format scenario names
# ---------------------------------------------------------

scenario_names = {
    "bau": "BAU",
    "levy": "Levy",
    "asis": "NZF as-is",
    "brazil": "Brazil",
    "liscr": "LISCR",
 #   "direct": "Direct"
}

df_change_long["Scenario"] = (
    df_change_long["Scenario"]
    .str.lower()
    .map(scenario_names)
)

# Exclude BAU and unknown scenarios
scenario_order = [
    "Levy",
    "NZF as-is",
    "Brazil",
    "LISCR",
#    "Direct"
]

df_change_long = df_change_long[
    df_change_long["Scenario"].isin(scenario_order)
].copy()


# ---------------------------------------------------------
# 25. Merge shares with CIF changes
# ---------------------------------------------------------

df_contribution = df_change_long.merge(
    df_share[["food_group", "Share"]],
    on="food_group",
    how="left",
    validate="many_to_one"
)

if (
    df_contribution["Share"].isna().any()
    or df_contribution["CIF_Change"].isna().any()
):
    st.error("Missing food group shares or CIF change values.")
    st.stop()

# Weighted percentage-point contribution
df_contribution["Contribution"] = (
    df_contribution["Share"]
    * df_contribution["CIF_Change"]
)
# Calculate total net contribution for each scenario and year
df_contribution["Total_Contribution"] = (
    df_contribution.groupby(["Scenario", "year"])["Contribution"]
    .transform("sum")
)

# Calculate each food group's percentage contribution
df_contribution["Pct_Contribution"] = (
    df_contribution["Contribution"]
    / df_contribution["Total_Contribution"].replace(0, float("nan"))
    * 100
)

# ---------------------------------------------------------
# 26. Prepare plotting data
# ---------------------------------------------------------

df_contribution["Year_Label"] = (
    df_contribution["year"].astype(str)
)

df_contribution["Scenario"] = pd.Categorical(
    df_contribution["Scenario"],
    categories=scenario_order,
    ordered=True
)

df_contribution = df_contribution.sort_values(
    ["year", "Scenario", "food_group"]
)

food_groups = sorted(
    df_contribution["food_group"].unique()
)

# Consistent colour assigned to each food group
colors = px.colors.qualitative.Plotly

food_colors = {
    group: colors[i % len(colors)]
    for i, group in enumerate(food_groups)
}


# ---------------------------------------------------------
# 27. Create diverging stacked bar chart
# ---------------------------------------------------------

fig_contribution = go.Figure()

for group in food_groups:

    group_df = df_contribution[
        df_contribution["food_group"] == group
    ].copy()

    fig_contribution.add_trace(
        go.Bar(
            x=[
                group_df["Year_Label"].tolist(),
                group_df["Scenario"].astype(str).tolist()
            ],
            y=group_df["Contribution"],
            name=group,
            marker_color=food_colors[group],
            customdata=group_df[
                ["Pct_Contribution", "Share", "CIF_Change"]
            ].to_numpy(),
            
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Contribution to Overall CIF Change: %{y:,.2f} pp<br>"
                "% Contribution: %{customdata[0]:,.2f}%<br>"
                "Food Import Value Share: %{customdata[1]:.1%}<br>"
                "Food Group CIF Change: %{customdata[2]:,.2f}%"
                "<extra></extra>"
            )
        )
    )


# ---------------------------------------------------------
# 28. Layout
# ---------------------------------------------------------

fig_contribution.update_layout(
    title="Food Group Contributions to Total CIF Change",
    barmode="relative",
    xaxis_title="Year / Scenario",
    yaxis_title="Contribution to CIF Change (percentage points)",
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
        b=120
    ),
    height=600
)

fig_contribution.update_yaxes(
    tickformat=",.2f",
    zeroline=True,
    zerolinecolor="grey",
    zerolinewidth=2
)

st.plotly_chart(
    fig_contribution,
    use_container_width=True
)
