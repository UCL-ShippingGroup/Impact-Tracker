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


"""
)


st.write(
"""


"""
)

st.subheader("Trade", divider='grey')

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

