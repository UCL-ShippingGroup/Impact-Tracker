
import streamlit as st
import pandas as pd
import plotly.express as px

from urllib.parse import quote
from country_selector import country_selector

country_selector()
st.set_page_config(layout='wide')

# ---------------------------------------------------------
# 1. Get selected country from home page
# ---------------------------------------------------------

selected_country = st.session_state.get(
    "iso_country",
    None
)

if not selected_country:
    st.warning(
        "Please select a country on the home page."
    )
    st.stop()

selected_country_iso = st.session_state.get(
    "iso_code",
    None
)

#

# ---------------------------------------------------------
# 2. Page title
# ---------------------------------------------------------

st.title("Seaborne Trade Portfolios")

st.write(
    """
    The country level Seabourne portfolio allows users to view a detailed break down of their import and export trade flows. Initial headline statistics offer a direct comparison between the overall 
    value of the original comtrade portfolio and what proportion was able to be captured through modelling, as well as offering a direct trade deficit insight. We also show the average weight per USD and 
    average distance to market as these are key indicators that are likely to drive higher NZF impacts if they are are high.  
    
    The first bar chart give a breakdown of the 25 largest trade flows, whilst the next two provide a breakdown by partner economy and HS2 commidity group.
    Further insight into the average weight per USD and distance to market by HS2 commidity group is also provided allowing users to see what major commodity trades are likely to drive up costs.
    Finally, a pie chart showing the value and weight proportion of each comodity within the total portfolio allows direct comparison between value and weight and how they match in terms of proportion of the portfolio.
    Further information about how these portfolios are derived can be found in the technical annex.
    """)


# meta_stats_d = {
#     "iso_code": "str", "iso_country": "str", "gdp": "str", 
#     #"comtrade_im_usd": "float", "im_val_usd": "float", "comtrade_ex_usd": "float", "comtrade_ex_usd": "float", 
# }
# meta_stats = pd.read_csv(
#     "https://raw.githubusercontent.com/UCL-ShippingGroup/Impact-Tracker/main/datasets/meta-stats.csv",
#     dtype=meta_stats_d
# )
# meta_stats_country = meta_stats[(meta_stats.iso_code == selected_country_iso)]
# #st.write(meta_stats_country)

# # print message regarding origin of trade data
# mot_inferred = "with Mode of Transport observed in the data rather than estimated" \
#     if "*" in meta_stats_country.import_portfolio.values[0] \
#     else "with Mode of Transport estimated from the data rather than observed"

# st.write(
#     "Trade data for {0} was sourced for the year {1} from the UN Comtrade platform, {2}.".format(
#         meta_stats_country.iso_country.values[0],
#         meta_stats_country.year.values[0],
#         mot_inferred
# ))

# st.write(
#     "The total value of imports modelled in the exercise is USD{0}, out of a total of USD{1} \
#     observed in the original Comtrade portfolio. An average of {2} kgs were associated with \
#     each USD of imported goods, with each kilogram travelling an average of {3} nautical miles.".format(
#         meta_stats_country.im_val_usd.values[0],
#         meta_stats_country.comtrade_im_usd.values[0],
#         meta_stats_country.im_WtV_kg_per_usd.values[0],
#         meta_stats_country.im_dist_to_market_nm.values[0]
# ))

# st.write(
#     "The total value of exports modelled in the exercise is USD{0}, out of a total of USD{1} \
#     observed in the original Comtrade portfolio. An average of {2} kgs were associated with \
#     each USD of exported goods, with each kilogram travelling an average of {3} nautical miles.".format(
#         meta_stats_country.ex_val_usd.values[0],
#         meta_stats_country.comtrade_ex_usd.values[0],
#         meta_stats_country.ex_WtV_kg_per_usd.values[0],
#         meta_stats_country.ex_dist_to_market_nm.values[0]
# ))
# ---------------------------------------------------------
# Load country metadata
# ---------------------------------------------------------

meta_stats_d = {
    "iso_code": "str",
    "iso_country": "str",
    "gdp": "str"
}

@st.cache_data
def load_meta_stats():
    return pd.read_csv(
        "https://raw.githubusercontent.com/"
        "UCL-ShippingGroup/Impact-Tracker/main/"
        "datasets/meta-stats.csv",
        dtype=meta_stats_d
    )

meta_stats = load_meta_stats()

# Ensure ISO code is consistently three digits
meta_stats["iso_code"] = (
    meta_stats["iso_code"].str.zfill(3)
)

selected_iso = str(selected_country_iso).zfill(3)

meta_stats_country = meta_stats[
    meta_stats["iso_code"] == selected_iso
]

if meta_stats_country.empty:
    st.warning(
        f"No trade metadata available for {selected_country}."
    )
    st.stop()

# Select the country's data
stats = meta_stats_country.iloc[0]


# ---------------------------------------------------------
# Clean numerical values
# ---------------------------------------------------------

def clean_number(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    # Remove common formatting characters
    value = (
        value
        .replace(",", "")
        .replace("$", "")
        .replace("USD", "")
        .replace("kg", "")
        .replace("nm", "")
        .strip()
    )

    return pd.to_numeric(value, errors="coerce")


# ---------------------------------------------------------
# Format currency
# ---------------------------------------------------------

def format_currency(value):

    value = clean_number(value)

    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1e9:
        return f"${value / 1e9:,.2f}bn"

    elif abs(value) >= 1e6:
        return f"${value / 1e6:,.2f}m"

    else:
        return f"${value:,.2f}"


# ---------------------------------------------------------
# Format other numbers
# ---------------------------------------------------------

def format_number(value, decimals=2):

    value = clean_number(value)

    if pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"

def modelled_percentage(modelled, original):

    modelled = clean_number(modelled)
    original = clean_number(original)

    if pd.isna(modelled) or pd.isna(original) or original == 0:
        return None

    percentage = modelled / original * 100

    return f"{percentage:.1f}% of original"

# ---------------------------------------------------------
# Trade data source information
# ---------------------------------------------------------

mot_inferred = (
    "Mode of Transport observed in the data"
    if "*" in str(stats["import_portfolio"])
    else "Mode of Transport estimated from the data rather than observed"
)

st.info(
    f"Trade data for **{stats['iso_country']}** "
    f"was sourced from UN Comtrade for **{stats['year']}**, "
    f"with {mot_inferred}."
)


# ---------------------------------------------------------
# Imports metrics
# ---------------------------------------------------------

st.subheader("Imports", divider="grey")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Modelled Import Value",
        value=format_currency(stats["im_val_usd"]),
        delta=modelled_percentage(
            stats["im_val_usd"],
            stats["comtrade_im_usd"]
        ),
        delta_color="off",
        border=True
    )

with col2:
    st.metric(
        label="Original Comtrade Value",
        value=format_currency(stats["comtrade_im_usd"]),
        border=True
    )

with col3:
    st.metric(
        label="Average Weight per USD",
        value=f"{format_number(stats['im_WtV_kg_per_usd'])} kg",
        border=True
    )

with col4:
    st.metric(
        label="Average Distance to Market",
        value=f"{format_number(stats['im_dist_to_market_nm'], 0)} nm",
        border=True
    )


# ---------------------------------------------------------
# Exports metrics
# ---------------------------------------------------------

st.subheader("Exports", divider="grey")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Modelled Export Value",
        value=format_currency(stats["ex_val_usd"]),
        delta=modelled_percentage(
            stats["ex_val_usd"],
            stats["comtrade_ex_usd"]
        ),
        delta_color="off",
        border=True
    )
with col2:
    st.metric(
        label="Original Comtrade Value",
        value=format_currency(stats["comtrade_ex_usd"]),
        border=True
    )

with col3:
    st.metric(
        label="Average Weight per USD",
        value=f"{format_number(stats['ex_WtV_kg_per_usd'])} kg",
        border=True
    )

with col4:
    st.metric(
        label="Average Distance to Market",
        value=f"{format_number(stats['ex_dist_to_market_nm'], 0)} nm",
        border=True
    )

st.subheader(
    f"Trade Portfolios for {selected_country}",
    divider="grey"
)


# ---------------------------------------------------------
# 3. Import / Export segmented control
# ---------------------------------------------------------

trade_flow = st.segmented_control(
    "Would you like to visualise Imports or Exports?",
    options=["Imports", "Exports"],
    default="Imports",
    key="trade_portfolio_flow"
)


# ---------------------------------------------------------
# 4. Value / Weight segmented control
# ---------------------------------------------------------

trade_measure = st.segmented_control(
    "Are you interested in trade value or weight?",
    options=["Value, $", "Weight, t"],
    default="Value, $",
    key="trade_portfolio_measure"
)


# ---------------------------------------------------------
# 5. Select dataset
# ---------------------------------------------------------

if trade_flow == "Imports":

    selected_file = "impact_im_v0.64.csv"

else:

    selected_file = "impact_ex_v0.64.csv"


# ---------------------------------------------------------
# 6.0 Load selected country's meta-data (JS edits)
# ---------------------------------------------------------










# ---------------------------------------------------------
# 6. Load selected country's data (Local Git LFS)
# ---------------------------------------------------------
# ---------------------------------------------------------
# 6. Load selected country's data (Local Git LFS)
# ---------------------------------------------------------

from pathlib import Path

# Get the directory where your Streamlit app is located
base_dir = Path(__file__).resolve().parent

@st.cache_data
def load_trade_data(country, iso_code, filename):

    # Ensure ISO code is three digits
    iso_code = str(iso_code).zfill(3)

    # Construct folder name: 008 - Albania
    country_folder = f"{iso_code} - {str(country).strip()}"

    # Construct the local file path
    file_path = (
        base_dir
        / "impact"
        / country_folder
        / filename
    )

    # Check whether the file exists
    if not file_path.is_file():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # Check whether Git LFS has downloaded
    # the actual CSV rather than just a pointer
    with open(file_path, "rb") as f:
        first_line = f.readline()

    if first_line.startswith(
        b"version https://git-lfs.github.com/spec/v1"
    ):
        raise RuntimeError(
            f"{filename} is still a Git LFS pointer. "
            "The actual CSV has not been downloaded."
        )

    # Read the actual CSV
    df = pd.read_csv(file_path)

    return df

# from pathlib import Path

# # Get the directory where your Streamlit app is located
# base_dir = Path(__file__).resolve().parent

# @st.cache_data
# def load_trade_data(country, filename):

#     # Construct the local file path
#     file_path = (
#         base_dir
#         / "impact"
#         / country
#         / filename
#     )

#     # Check whether the file exists
#     if not file_path.is_file():
#         raise FileNotFoundError(
#             f"File not found: {file_path}"
#         )

#     # Check whether Git LFS has downloaded
#     # the actual CSV rather than just a pointer
#     with open(file_path, "rb") as f:
#         first_line = f.readline()

#     if first_line.startswith(
#         b"version https://git-lfs.github.com/spec/v1"
#     ):
#         raise RuntimeError(
#             f"{filename} is still a Git LFS pointer. "
#             "The actual CSV has not been downloaded."
#         )

#     # Read the actual CSV
#     df = pd.read_csv(file_path)

#     return df
# from pathlib import Path

# base_dir = Path(__file__).resolve().parent

# st.write("### Data Loading Diagnostics")

# st.write("Current script:", __file__)
# st.write("Base directory:", str(base_dir))
# st.write("Selected country:", repr(selected_country))
# st.write("Selected file:", repr(selected_file))

# file_path = (
#     base_dir
#     / "impact"
#     / selected_country
#     / selected_file
# )

# st.write("Expected file path:", str(file_path))
# st.write("File exists:", file_path.is_file())

# if file_path.is_file():

#     st.write(
#         "File size:",
#         f"{file_path.stat().st_size / 1e6:,.2f} MB"
#     )

#     with open(file_path, "rb") as f:
#         first_line = f.readline()

#     st.write(
#         "Git LFS pointer:",
#         first_line.startswith(
#             b"version https://git-lfs.github.com/spec/v1"
#         )
#     )

# else:

#     st.write("Parent folder exists:", file_path.parent.is_dir())

#     if file_path.parent.is_dir():
#         st.write(
#             "Files available:",
#             [p.name for p in file_path.parent.iterdir()]
#         )

try:

    df = load_trade_data(
        selected_country,
        selected_country_iso,
        selected_file
    )

except (FileNotFoundError, RuntimeError, OSError) as e:

    st.error(
        f"Could not load trade data for {selected_country}: {e}"
    )

    st.stop()


# ---------------------------------------------------------
# 7. Determine column and units
# ---------------------------------------------------------

if trade_measure == "Value, $":

    if trade_flow == "Imports":
        value_col = "cifvalue"
    else:
        value_col = "fobvalue"

    value_title = "Trade Value (Million USD)"
    unit = "Million USD"

else:

    value_col = "vol_kg_vtw"

    value_title = "Trade Weight (tonnes)"
    unit = "t"


# ---------------------------------------------------------
# 8. Prepare data
# ---------------------------------------------------------

df = df.copy()

# Ensure selected column is numeric
df[value_col] = pd.to_numeric(
    df[value_col],
    errors="coerce"
)

# Remove missing values
df = df.dropna(
    subset=[value_col]
)

# Convert values to the appropriate units
if trade_measure == "Weight, t":

    # Convert kilograms to tonnes
    df["Plot_Value"] = df[value_col] / 1000

else:

    # Convert USD to million USD
    df["Plot_Value"] = df[value_col] / 1e6

# ---------------------------------------------------------
# 9. Function to aggregate top 25 categories
# ---------------------------------------------------------

def prepare_top25(data, group_col):

    plot_df = data.copy()

    # Remove missing categories
    plot_df = plot_df.dropna(
        subset=[group_col]
    )

    # Sum values by category
    plot_df = (
        plot_df
        .groupby(
            group_col,
            as_index=False
        )["Plot_Value"]
        .sum()
    )

    # Sort descending and select top 25
    plot_df = (
        plot_df
        .sort_values(
            "Plot_Value",
            ascending=False
        )
        .head(25)
        .copy()
    )

    return plot_df


# ---------------------------------------------------------
# 10. Chart formatting function
# ---------------------------------------------------------

def create_trade_bar_chart(
    data,
    group_col,
    chart_title
):

    plot_df = prepare_top25(
        data,
        group_col
    )

    if plot_df.empty:
        return None

    # Set order of categories
    category_order = (
        plot_df[group_col].tolist()
    )

    # Create bar chart
    fig = px.bar(

        plot_df,

        x=group_col,
        y="Plot_Value",

        color="Plot_Value",

        color_continuous_scale="Blues",

        range_color=(
            0,
            max(plot_df["Plot_Value"].max(), 1)
        ),

        category_orders={
            group_col: category_order
        },

        labels={
            group_col: "",
            "Plot_Value": value_title
        }
    )

    # ---------------------------------------------
    # Hover formatting
    # ---------------------------------------------

    if trade_measure == "Value, $":

        hover_format = "$%{y:,.2f} million"

    else:

        hover_format = "%{y:,.2f} t"

    fig.update_traces(

        hovertemplate=(
            "<b>%{x}</b><br>"
            + value_title + ": "
            + hover_format
            + "<extra></extra>"
        ),

        marker_line_width=0
    )

    # ---------------------------------------------
    # Layout
    # ---------------------------------------------

    fig.update_layout(

        height=600,

        template="plotly_white",

        title=dict(
            text=chart_title,
            x=0.5,
            xanchor="center"
        ),

        margin=dict(
            l=80,
            r=30,
            t=70,
            b=160
        ),

        showlegend=False,

        coloraxis_showscale=False,

        hovermode="closest",

        xaxis=dict(
            title=None,

            tickangle=-45,

            categoryorder="array",
            categoryarray=category_order,

            showgrid=False,

            tickfont=dict(
                size=11
            ),

            automargin=True
        ),

        yaxis=dict(
            title=value_title,

            showgrid=True,

            gridcolor="rgba(200,200,200,0.3)",

            zeroline=True,
            zerolinecolor="lightgrey",

            rangemode="tozero"
        )
    )

    # ---------------------------------------------
    # Y-axis currency or weight formatting
    # ---------------------------------------------

    if trade_measure == "Value, $":

        hover_format = "$%{y:,.2f} million"

    else:

        hover_format = "%{y:,.2f} t"

    return fig


# ---------------------------------------------------------
# 11. Chart 1 - Top trade flows
# ---------------------------------------------------------

st.markdown(
    f"### Top {trade_flow} Trade Flows"
)

fig_flows = create_trade_bar_chart(
    df,
    "HS2_bilat_desc",
    f"Top 25 {trade_flow} Trade Flows"
)

if fig_flows is not None:

    st.plotly_chart(
        fig_flows,
        use_container_width=True,
        key="trade_portfolio_flows"
    )

else:

    st.info("No trade flow data available.")





# ---------------------------------------------------------
# 13. Chart 3 - Top partner countries
# ---------------------------------------------------------

st.markdown(
    f"### Top {trade_flow} Partner Countries"
)

fig_partners = create_trade_bar_chart(
    df,
    "partnerDesc",
    f"Top 25 {trade_flow} Partner Countries"
)

if fig_partners is not None:

    st.plotly_chart(
        fig_partners,
        use_container_width=True,
        key="trade_portfolio_partners"
    )

else:

    st.info("No partner country data available.")


# ---------------------------------------------------------
# 12. Chart 2 - Top HS2 commodity flows
# ---------------------------------------------------------

st.markdown(
    f"### Top {trade_flow} HS2 Commodity Flows"
)

fig_commodities = create_trade_bar_chart(
    df,
    "HS2_desc",
    f"Top 25 {trade_flow} HS2 Commodity Flows"
)

if fig_commodities is not None:

    st.plotly_chart(
        fig_commodities,
        use_container_width=True,
        key="trade_portfolio_commodities"
    )

else:

    st.info("No commodity data available.")


# ---------------------------------------------------------
# 14. Average Weight per USD / Distance to Market
# ---------------------------------------------------------

st.subheader(
    "Trade Characteristics by HS2 Commodity",
    divider="grey"
)

# ---------------------------------------------------------
# 14.1 Segment controls
# ---------------------------------------------------------

characteristic_flow = st.segmented_control(
    "Would you like to visualise Imports or Exports?",
    options=["Imports", "Exports"],
    default="Imports",
    key="characteristic_flow"
)

characteristic_measure = st.segmented_control(
    "Which measure are you interested in?",
    options=[
        "Average Weight per USD",
        "Average Distance to Market"
    ],
    default="Average Weight per USD",
    key="characteristic_measure"
)

# ---------------------------------------------------------
# 14.2 Select dataset and trade value column
# ---------------------------------------------------------

if characteristic_flow == "Imports":

    characteristic_file = "hs2_total_usd_im_v0.64.csv"
    trade_value_col = "cifvalue"
    trade_value_label = "CIF Value"

else:

    characteristic_file = "hs2_total_usd_ex_v0.64.csv"
    trade_value_col = "fobvalue"
    trade_value_label = "FOB Value"


# ---------------------------------------------------------
# 14.3 Load selected country's data
# ---------------------------------------------------------

@st.cache_data
def load_hs2_characteristics(country, iso_code, filename):

    iso_code = str(iso_code).zfill(3)

    country_folder = f"{iso_code} - {str(country).strip()}"

    file_path = (
        base_dir
        / "impact"
        / country_folder
        / "results"
        / filename
    )

    if not file_path.is_file():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return pd.read_csv(file_path)


try:

    df_characteristics = load_hs2_characteristics(
        selected_country,
        selected_country_iso,
        characteristic_file
    )

except (FileNotFoundError, OSError) as e:

    st.error(
        f"Could not load HS2 data for {selected_country}: {e}"
    )

    st.stop()


# ---------------------------------------------------------
# 14.4 Select measure
# ---------------------------------------------------------

if characteristic_measure == "Average Weight per USD":

    measure_col = "kg_per_usd_netWgt"
    measure_label = "Average Weight per USD (kg/USD)"
    measure_unit = "kg/USD"

else:

    measure_col = "sea_dist_nm"
    measure_label = "Average Distance to Market (nm)"
    measure_unit = "nm"


# ---------------------------------------------------------
# 14.5 Prepare data
# ---------------------------------------------------------

plot_df = df_characteristics.copy()

# Convert columns to numeric
for col in [trade_value_col, measure_col]:

    plot_df[col] = pd.to_numeric(
        plot_df[col],
        errors="coerce"
    )

# Remove rows with missing values
plot_df = plot_df.dropna(
    subset=[
        "HS2_desc",
        trade_value_col,
        measure_col
    ]
)

# Sort by CIF/FOB value and select top 25
plot_df = (
    plot_df
    .sort_values(
        trade_value_col,
        ascending=False
    )
    .head(25)
    .copy()
)

# Convert trade value to millions for hover
plot_df["Trade_Value_Million"] = (
    plot_df[trade_value_col] / 1e6
)

# Preserve trade value ranking on x-axis
category_order = plot_df["HS2_desc"].tolist()


# ---------------------------------------------------------
# 14.6 Create bar chart
# ---------------------------------------------------------

fig = px.bar(

    plot_df,

    x="HS2_desc",
    y=measure_col,

    color=trade_value_col,

    color_continuous_scale="Blues",

    category_orders={
        "HS2_desc": category_order
    },

    custom_data=[
        "Trade_Value_Million"
    ],

    labels={
        "HS2_desc": "",
        measure_col: measure_label
    }

)


# ---------------------------------------------------------
# 14.7 Hover formatting
# ---------------------------------------------------------

fig.update_traces(

    hovertemplate=(
        "<b>%{x}</b><br>"
        + measure_label
        + ": %{y:,.2f} "
        + measure_unit
        + "<br>"
        + trade_value_label
        + ": $%{customdata[0]:,.2f} million"
        + "<extra></extra>"
    ),

    marker_line_width=0
)


# ---------------------------------------------------------
# 14.8 Chart layout
# ---------------------------------------------------------

fig.update_layout(

    height=600,

    template="plotly_white",

    title=dict(
        text=(
            f"Top 25 {characteristic_flow} HS2 Commodities"
            f" - {characteristic_measure}"
        ),
        x=0.5,
        xanchor="center"
    ),

    margin=dict(
        l=80,
        r=30,
        t=70,
        b=160
    ),

    showlegend=False,

    coloraxis_showscale=False,

    hovermode="closest",

    xaxis=dict(
        title=None,
        tickangle=-45,
        categoryorder="array",
        categoryarray=category_order,
        showgrid=False,
        tickfont=dict(size=11),
        automargin=True
    ),

    yaxis=dict(
        title=measure_label,
        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)",
        zeroline=True,
        zerolinecolor="lightgrey",
        rangemode="tozero"
    )

)


# ---------------------------------------------------------
# 14.9 Display chart
# ---------------------------------------------------------

if not plot_df.empty:

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="hs2_trade_characteristics"
    )

else:

    st.info(
        "No HS2 trade characteristics data available."
    )


# ---------------------------------------------------------
# 15. HS2 Trade Composition - Value and Net Weight
# ---------------------------------------------------------

st.subheader(
    "HS2 Trade Composition",
    divider="grey"
)

# ---------------------------------------------------------
# 15.1 Prepare data
# ---------------------------------------------------------

pie_df = df_characteristics.copy()

# Convert numerical columns
for col in [trade_value_col, "pct_val", "pct_net_wgt"]:

    pie_df[col] = pd.to_numeric(
        pie_df[col],
        errors="coerce"
    )

# Remove missing HS2 categories
pie_df = pie_df.dropna(subset=["HS2_desc"])

# Aggregate by HS2 category
pie_df = (
    pie_df
    .groupby("HS2_desc", as_index=False)
    .agg({
        trade_value_col: "sum",
        "pct_val": "sum",
        "pct_net_wgt": "sum"
    })
)

# Sort by CIF/FOB value
pie_df = pie_df.sort_values(
    trade_value_col,
    ascending=False
)

# Identify top 25 HS2 categories
top25_categories = (
    pie_df.head(25)["HS2_desc"].tolist()
)

# Assign all remaining categories to Other
pie_df["Commodity"] = pie_df["HS2_desc"].where(
    pie_df["HS2_desc"].isin(top25_categories),
    "Other HS2 Commodities"
)

# Group remaining categories together
pie_df = (
    pie_df
    .groupby("Commodity", as_index=False)
    .agg({
        "pct_val": "sum",
        "pct_net_wgt": "sum"
    })
)

# Keep the top 25 in trade value order
category_order = top25_categories.copy()

if "Other HS2 Commodities" in pie_df["Commodity"].values:
    category_order.append("Other HS2 Commodities")

pie_df["Commodity"] = pd.Categorical(
    pie_df["Commodity"],
    categories=category_order,
    ordered=True
)

pie_df = pie_df.sort_values("Commodity")


# ---------------------------------------------------------
# 15.2 Function to create pie charts
# ---------------------------------------------------------

def create_hs2_pie_chart(data, value_col, chart_title):

    chart_df = data[
        ["Commodity", value_col]
    ].copy()

    chart_df = chart_df.dropna(subset=[value_col])

    chart_df = chart_df[
        chart_df[value_col] > 0
    ]

    if chart_df.empty:
        return None

    fig = px.pie(
        chart_df,
        names="Commodity",
        values=value_col,
        hole=0,
        color_discrete_sequence=px.colors.qualitative.Alphabet
    )

    fig.update_traces(

        textinfo="percent",

        textposition="inside",

        hovertemplate=(
            "<b>%{label}</b><br>"
            "Share: %{value:.2f}%"
            "<extra></extra>"
        ),

        sort=False
    )

    fig.update_layout(

        title=dict(
            text=chart_title,
            x=0.5,
            xanchor="center"
        ),

        height=650,

        template="plotly_white",

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )

    return fig


# ---------------------------------------------------------
# 15.3 Create two pie charts side by side
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig_value = create_hs2_pie_chart(
        pie_df,
        "pct_val",
        f"{characteristic_flow} - Share of Trade Value"
    )

    if fig_value is not None:

        st.plotly_chart(
            fig_value,
            use_container_width=True,
            key="hs2_value_pie"
        )

    else:

        st.info("No trade value data available.")


with col2:

    fig_weight = create_hs2_pie_chart(
        pie_df,
        "pct_net_wgt",
        f"{characteristic_flow} - Share of Net Weight"
    )

    if fig_weight is not None:

        st.plotly_chart(
            fig_weight,
            use_container_width=True,
            key="hs2_weight_pie"
        )

    else:

        st.info("No net weight data available.")

