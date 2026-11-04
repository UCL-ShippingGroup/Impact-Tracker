import pandas as pd
import requests
from io import StringIO
import streamlit as st
#st.markdown("##### Contact")
st.title("Technical Annex")

selected_country_iso = st.session_state.get(
    "iso_code",
    None
)

st.write("'selected_country_iso': ", selected_country_iso)

#base_url = "https://raw.githubusercontent.com/UCL-ShippingGroup/Impact-Tracker/main/datasets/"
meta_stats_d = {"iso_code": "str", "iso_country": "str"}
meta_stats = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/Impact-Tracker/main/datasets/meta-stats.csv")
st.write(meta_stats.head(2))

meta_stats_country = meta_stats[(meta_stats.iso_code == selected_country_iso)]
for idx, row in meta_stats_country:
    pass

st.write(row)

st.write(
"""
Building upon methods developed during the IMO-led Comprehensive Impact Assessment process, 
the supporting methodology combines bespoke trade statistics with international vessel voyage 
data to estimate NZF economic impacts on individual trade flows comprising both the import- 
and export-side trade portfolios. The skeleton of the approach builds on the impact assessment 
methodology pioneered during Task 4 of the IMO-led Comprehensive Impact Assessment (CIA) 
(Starcrest, 2024). Fully documented in its own paper (Fricaudet et al, 2026), the analysis 
starts with inputs derived from techno-economic modelling of the cost impacts of alternative 
proposed policy measures on individual vessels, as well as how these cost impacts are expected 
to drive uptake of alternative technologies and ultimately lead to the evolution of the global 
fleet. By linking individual import records with expected changes in maritime transport costs, 
a detailed understanding of how each of the proposed policy measures will impact on prices paid 
for alternative food groups may be derived.

"""
)


st.subheader("Maritime Transport", divider='grey')

st.write(
"""
First, techno-economic modelling outputs are sourced from UCL’s Fleet Evolution Model (Fricaudet 
et al, 2026). This type of modelling is concerned approximating investment decisions on whether 
to scrap or continue operating a vessel, as well as whether to invest in energy efficiency or 
deep transitional technologies such as engine conversions or retrofits, depending on prevailing 
economic conditions such as the existence of decarbonisation regulations. Results taken from the 
model are provided in terms of the transport costs associated with the provision of transport 
capacity for one tonne of goods to be moved across one nautical mile. The results are 
re-formatted in terms of expected future transport costs across nine future years and 30 unique 
vessel classes. The following six policy options are modelled:

1. Business as Usual, where no IMO policy is adopted.
2. NZF ‘as levy’
3. NZF 'as is'
4. Brazil’s softer start, intense finish proposal
5. LISCR concept
6. NZF with Direct Contribution

"""
)


st.write(
"""
Cost intensities representing the policy scenarios described above are then applied to a dataset 
of international voyages derived during the 4th IMO GHG Study and covering the year 2018. In its 
initial form, the dataset contains 2.7 million records describing the voyages of 59 thousand unique 
vessels between 215 countries. Since the dataset covers nearly all types of vessel installed with 
AIS transponders, it is first filtered for the merchant vessel classes modelled in the FEM, 
resulting in a final dataset of 1.1 million voyage records (40.3% of the original) and representing 
544.7 million tonnes of carbon dioxide emissions. Cost intensities are merged onto this filtered 
voyages dataset, resulting in a final output table of vessel voyages complete with origin-destination 
labels, start-end timestamps and fields representing distances travelled, energy demand, fuel 
consumption and GHG emissions associated with each voyage, as well as 63 data fields capturing cost 
intensities per policy scenario and future year specific to the vessel’s class.
"""
)

st.subheader("Trade", divider='grey')

st.write(
"""
International trade datasets representing the imports and exports of each country are sourced from 
the UN Comtrade platform for a representative year. The UN Comtrade database represents the most 
comprehensive source of detailed international trade data available worldwide, offering near-universal 
access to aggregate trade statistics covering around 92% of the world’s merchandise trade by value. 
Depending on the availability of trade records on the Comtrade platform for a given country, a range 
of data processing steps are applied in order to derive consistent seaborne trade portfolios across 
the countries included. 
"""
)

st.write(
"""
Although often not submitted to the Comtrade platform, disaggregation of trade volumes by transport 
mode is essential for accurate isolation of the seaborne component of trade. When selecting an 
appropriate year from which to source trade statistics, a recent year where transport mode information 
has been provided is selected. Where transport mode information isn’t available, trade statistics 
across all transport modes for a recent year are first downloaded, and a mode split model is applied 
to isolate the seaborne component based on observations from the UNCTAD Trade-and-Transport database 
(UNCTAD, 2025). 
"""
)

st.write(
"""
Once the seaborne trade portfolio for a country has been downloaded and any necessary processing steps 
completed, it is read into a python-based Jupyter notebook for analysis. The first step is to format 
the dataset, performing actions such as ensuring country ISO codes and Harmonised System commodity 
codes are formatted correctly, as well as deriving new fields for concisely categorising individual 
bilateral trade records. Given inconsistencies in the way weight is recorded within Comtrade, a new 
weight field is established based on the average value-to-weight ratio observed per HS 4-digit commodity 
heading across publications of the CEPII BACI dataset covering the years 2017-23. Another additional step 
introduces one or more vessel types identified as likely to facilitate transportation of each specific 
commodity type. To achieve this, a dataset of consignment-level Bills of Lading data from the Global 
Shipping Watch project (Schim van der Loeff et al, 2018) is introduced to understand which vessel types 
are most prevalent in facilitating the transportation of goods under alternative commodity headings. 
"""
)

st.write(
"""

The final step of the trade process is to derive an assumed distance associated with each bilateral trade 
record based on its specific origin-destination country pairing. The estimation of distance between bilateral 
country pairs is sourced from the CERDI ‘Sea-distances’ table, further information for which can be found in 
(Bertoli et al, 2016). With the assumed sea distance per bilateral trade record now established as a new data 
field to the seaborne trade portfolio dataset, the assumption is taken that the cargo mass travels this 
distance as it transits from origin to destination country. This assumption represents a lower-bound on the 
total distance a trade is likely to travel as it doesn’t consider multiple stop or transshipment practises, 
and therefore represents a limitation in the study. Nevertheless, derivation of an assumed distance in this 
way does enable for the calculation of ‘transport work’ associated with each bilateral trade record to be 
undertaken, denoting the product of cargo volume and distance travelled. The trade portfolio generation step 
is performed on both the importer and exporter side for each country.
"""
)


st.subheader("Impact Assessment", divider='grey')

st.write(
"""
The final process seeks to combine the seaborne trade portfolios with voyage-level cost intensities to estimate 
the specific costs associated with each bilateral trade record. Using these subsets of the voyages table, the 
importer- and exporter-side seaborne trade datasets are iterated through and, for each trade record, an 
appropriate sample of voyages is sought that is deemed most likely to facilitate the specific trade. A single 
uniform method isn’t possible to apply in all cases, and so a staggered algorithmic approach is instead used to 
derive the most appropriate subset of observed voyages for each bilateral commodity trade. Although convoluted, 
the intention of this process is to generate bespoke cost intensity values for each trade record based on unique 
trends of the country’s shipping activity, as these may differ greatly from global averages. 
"""
)

st.write(
"""
The final transport costs associated with each bilateral trade record can now be evaluated by combining each 
voyage’s transport work with the averaged cost intensities observed from representative shipping activity. These 
transport costs are evaluated in US dollars in accordance with the six alternative policy options and nine future 
target years. In terms of food security, a final step isolates results for commodity codes associated with key 
individual food groups as applied in (Forengie et al, 2025). The aggregate cost impact is evaluated and expressed 
in relation to the CIF price to represent the overall price impact per food group and country for each policy 
scenario across future years to 2050.
"""
)

st.subheader("References", divider='grey')

st.write(
"""
Bertoli et al. (2016). The CERDI-seadistance database. Centre d’Etudes et de Reserches sur le Developpement 
International. Available at: https://shs.hal.science/halshs-01288748v1.    

Faber et al. (2020). Fourth IMO GHG Study. London, UK.    

Forengie et al. (2025). Assessing the Potential Impact of the IMO Mid-Term GHG Mitigation Measures on Food Security 
in Caribbean Nations.     

Fricaudet et al. (upcoming). Beyond cost-optimal transitions: behavioural decision-making and policy feedbacks in 
shipping decarbonisation.     

Schim van der Loeff et al. (2018). A spatially explicit data-driven approach to calculating commodity-specific 
shipping emissions per vessel. Available at: https://doi.org/10.1016/j.jclepro.2018.09.053.    

Starcrest. (2024). Report of the comprehensive impact assessment of the basket of candidate GHG reduction mid-term 
measures full report on Task 4 - Final Draft. MEPC 82/INF.8/Add.3.    

UNCTAD. (2025). Trade-and-Transport Dataset - Documentation.    

"""
)

