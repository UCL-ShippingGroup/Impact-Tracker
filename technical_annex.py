import pandas as pd
import requests
from io import StringIO
import streamlit as st
#st.markdown("##### Contact")
st.subheader("Technical Annex", divider='grey')

st.markdown("""
<style>
    .big-font {font-size:6px !important;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    # '<p class="big-font">Hello World !!</p>'
    '<p class="big-font">
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
    </p>'
)

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
