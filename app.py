import streamlit as st
import pandas as pd
import numpy as np

import folium
import streamlit_folium
from streamlit_folium import st_folium, folium_static

from methods import ZipMap, TimeLapse, read_data

import plotly
import chart_studio.plotly as py
from plotly import graph_objs as go

#Build App
#App Code 

def main():
    ########################################################################################################
    #PRELIMINARY

    #Set App title and caption
    app_title = 'Crime Density Arlington VA (2016-2024)'
    #caption = 'Data derived from Arlington County Daily Crime Report:\nhttps://www.arlingtonva.us/About-Arlington/Newsroom?dlv_ARL%20CL%20Public%20News%20Listing%20without%20Image=(dd_OC%20News%20Categories=Daily%20Crime%20Report)'

    st.set_page_config(app_title, layout='wide')
    st.title(app_title)
    st.markdown("""Data derived from [Arlington County Daily Crime Report](https://www.arlingtonva.us/About-Arlington/Newsroom?dlv_ARL%20CL%20Public%20News%20Listing%20without%20Image=(dd_OC%20News%20Categories=Daily%20Crime%20Report))""")

    #st.caption(caption)
    #st.write(caption)

    #Read in data
    data = read_data('final_data.csv')

    #Create sidebar
    menu = ["Crime Density by Zip Code", "Crime Density Timelapse"]
    choice = st.sidebar.selectbox("Menu", menu)

    ######################################################################################################
    #ZIP CODE + FORECASTING TAB

    if choice == 'Crime Density by Zip Code':

        #Interactive About Bar    
        about_bar = st.expander("**About This Section**")
        about_bar.markdown("""
                           * Select different Crime Types below to filter for specified crime density by Zip Code
                           * **Click a ZIP Code on the map to forecast crime density for that region**, using both Crime Type and Forecast Period as filters.
                        """)
        
        #Crime Filtering
        select1, select2 = st.columns(2)
        with select1:
            crime_selection = ['All Crimes', 'Crimes Against Person', 'Crimes Against Property', 'Crimes Against Society']
            select_crimes = st.selectbox("Crime Type", crime_selection)

        with select2:
           
            forecast_selection = [1, 3, 4, 6, 12, 24]
            default_i = forecast_selection.index(12)
            select_fcst = st.selectbox("Forecast Period (Months)", forecast_selection, index=default_i)

        #Filter based on Crime Type
        if select_crimes == 'All Crimes':
            df = data
        else:
            df = data[data['Crime_Category'] == select_crimes]

        #Initiate ZipMap() Class & prepare data for viz
        zm = ZipMap(df)

        zips = zm.aggregate_zips()
        
        #Geojson for zipcode borders - check
        geojson = 'va_zip_geo.json'
        geojson_df = zm.geojson_zips(geojson)

        #Parameters for FBProphet model
        params = zm.get_params()

        #Display as side by side col containers 
        col1, col2 = st.columns(2)

        with col1:
            #Folium map
            zip_map = zm.create_map(zips, geojson_df)
            #st_map = st_folium(zip_map, width=700, height=525)
            st_map = st_folium(zip_map, width=700, height=600)

        with col2:
            #Access clickable forecasting
            if st_map['last_active_drawing']:
                #st.write(st_map['last_active_drawing']['properties']['ZCTA5CE10'])
                click_zip = str(st_map['last_active_drawing']['properties']['ZCTA5CE10'])

                fcst_df, fcst_plot, components = zm.prophet_forecast(params, click_zip, select_crimes, select_fcst)
                st.plotly_chart(fcst_plot, use_container_width=True, theme=None)

    ######################################################################################################
    #TIMELAPSE + SPATIOTEMPORAL FORECASTING

    if choice == 'Crime Density Timelapse':
        #Interactive About Bar    
        about_bar = st.expander("**About This Section**")
        about_bar.markdown("""
                            * Select Map Type and Timeframe to build your own Timelapse Map - Click 'Render Map' to view.
                           * Press play once the map has rendered to view how crime density trends have changed over time
                           
                        """)
        
        #Centred selectbox for all options
        crime_selection = ['All Crimes', 'Crimes Against Person', 'Crimes Against Property', 'Crimes Against Society']
        select_crimes = st.selectbox("Crime Type", crime_selection)

        #Crime Filtering
        select1, select2 = st.columns(2)
        with select1:
            map_type = ['Heatmap'] #, 'Point Map']
            select_crimes = st.selectbox("Choose Map Type", map_type)

        with select2:
            if select_crimes == 'Heatmap':
                date_range = ['Monthly', 'Yearly', 'Monthly Aggregated', 'Day Of Week']
            
            elif select_crimes == 'Point Map':
                date_range = ['Daily (Last 30 Days) + Forecast']

            select_dr = st.selectbox("Choose Timelapse Timeframe", date_range)

        #Initialize TimeLapse() class
        tl = TimeLapse(data)

        #Filter based on Crime Type
        if select_crimes == 'All Crimes':
            df = data
        else:
            df = data[data['Crime_Category'] == select_crimes]

        render_map = st.button("Render Map")
        if render_map:

            if select_dr == 'Monthly':
                data_list, time_index = tl.year_month()
            
            elif select_dr == 'Yearly':
                data_list, time_index = tl.yearly()

            elif select_dr == 'Day Of Week':
                data_list, time_index = tl.dow()

            elif select_dr == 'Monthly Aggregated':
                data_list, time_index = tl.agg_month()

            tl_map = tl.create_timelapse(data_list, time_index)
            st_map_tl = folium_static(tl_map, width=1400, height=525)


if __name__ == "__main__":
    main()