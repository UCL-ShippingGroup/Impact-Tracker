st.set_page_config(layout='wide')
st.title('Global Overview')

st.segmented_control(
      "Which scenario would you like to Explore?",
      options,
      default = "'as-is'")

st.segmented_control(



fig = px.choropleth(
    plot_df,
    locations="alpha-3",
    locationmode="ISO-3",
    color=selected_column,
    hover_name='alpha-3',
    animation_frame='year',
    color_continuous_scale="Reds",
    labels={selected_column: unit},
    title=f"{chart_choice2} — {chart_choice3} — {chart_choice4} — {chart_choice}"
)
fig.update_layout(paper_bgcolor="white",height= 600, width=400,font_size=18)
fig.update_geos(
    showcoastlines=True,
    coastlinecolor="Black",
    #showland=True,
    showcountries=True,
    countrycolor="gray",
    fitbounds="locations"
)
st.plotly_chart(
    fig,
    width='stretch'
)
