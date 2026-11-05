
import streamlit as st
import pandas as pd
import plotly.express as px

from urllib.parse import quote

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




meta_stats_d = {
    "iso_code": "str", "iso_country": "str", "gdp": "str", 
    #"comtrade_im_usd": "float", "im_val_usd": "float", "comtrade_ex_usd": "float", "comtrade_ex_usd": "float", 
}
meta_stats = pd.read_csv(
    "https://raw.githubusercontent.com/UCL-ShippingGroup/Impact-Tracker/main/datasets/meta-stats.csv",
    dtype=meta_stats_d
)
meta_stats_country = meta_stats[(meta_stats.iso_code == selected_country_iso)]
#st.write(meta_stats_country)

# print message regarding origin of trade data
mot_inferred = "with Mode of Transport observed in the data rather than estimated" \
    if "*" in meta_stats_country.import_portfolio.values[0] \
    else "with Mode of Transport estimated from the data rather than observed"

st.write(
    "Trade data for {0} was sourced for the year {1} from the UN Comtrade platform, {2}.".format(
        meta_stats_country.iso_country.values[0],
        meta_stats_country.year.values[0],
        mot_inferred
))

st.write(
    "The total value of imports modelled in the exercise is USD{0}, out of a total of USD{1} \
    observed in the original Comtrade portfolio. An average of {2} kgs were associated with \
    each USD of imported goods, with each kilogram travelling an average of {3} nautical miles.".format(
        meta_stats_country.im_val_usd.values[0],
        meta_stats_country.comtrade_im_usd.values[0],
        meta_stats_country.im_WtV_kg_per_usd.values[0],
        meta_stats_country.im_dist_to_market_nm.values[0]
))

st.write(
    "The total value of exports modelled in the exercise is USD{0}, out of a total of USD{1} \
    observed in the original Comtrade portfolio. An average of {2} kgs were associated with \
    each USD of exported goods, with each kilogram travelling an average of {3} nautical miles.".format(
        meta_stats_country.ex_val_usd.values[0],
        meta_stats_country.comtrade_ex_usd.values[0],
        meta_stats_country.ex_WtV_kg_per_usd.values[0],
        meta_stats_country.ex_dist_to_market_nm.values[0]
))
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
    else "Mode of Transport estimated from the data"
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
