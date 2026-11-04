import pandas as pd
import requests
from io import StringIO
import streamlit as st
#st.markdown("##### Contact")
st.subheader("Technical Annex", divider='grey')

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


"""
)

st.write(
"""


"""
)

st.write(
"""


"""
)




st.subheader("Impact Assessment", divider='grey')

st.write(
"""


"""
)

st.write(
"""


"""
)


st.subheader("References", divider='grey')

st.write(
"""


"""
)

