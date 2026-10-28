
import streamlit as st
import pandas as pd
import plotly.express as px

from urllib.parse import quote

st.set_page_config(layout='wide')
st.title('Seabourne Trade Portfolios')
st.divider()
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


# ---------------------------------------------------------
# 2. Page title
# ---------------------------------------------------------

st.title("Seabourne Trade Portfolios")

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
# 6. Load selected country's data
# ---------------------------------------------------------

# ---------------------------------------------------------
# 6. Load selected country's data (Local Git LFS)
# ---------------------------------------------------------

from pathlib import Path

# Get the directory where your Streamlit app is located
base_dir = Path(__file__).resolve().parent

@st.cache_data
def load_trade_data(country, filename):

    # Construct the local file path
    file_path = (
        base_dir
        / "impact"
        / country
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


try:

    df = load_trade_data(
        selected_country,
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

    value_title = "Trade Value (USD)"
    unit = "$"

else:

    value_col = "vol_kg_vtw_comp"

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

# Convert kilograms to tonnes
if trade_measure == "Weight, t":

    df["Plot_Value"] = df[value_col] / 1000

else:

    df["Plot_Value"] = df[value_col]


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

        hover_format = "$%{y:,.2f}"

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

        fig.update_yaxes(
            tickformat=",.2s",
            tickprefix="$"
        )

    else:

        fig.update_yaxes(
            tickformat=",.2s",
            ticksuffix=" t"
        )

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
