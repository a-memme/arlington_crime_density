# Arlington Crime Density - 2016 to Feb 2024
*Exploration, analysis and forecasting of crime density in Arlington VA from 2016-2024.*

*Cumulative Masters Program Project (Georgia Institude of Technology Masters of Science in Analytics) by Andrew Memme, Evan Nunez, James McMullen, Curtis Wideman, and Lukas Santoso*

## Instructions 
Click the link below to interact with our Crime Density Dashboard. Two tabs display interactive visualizations focusing on predictive crime density, and how trends have changed over time and space:

[Crime Density Dashboard](https://arlingtoncrimedensity2016-2024.streamlit.app/)

### Crime Density by Zip Code 
- Use this tab to view cumulative crime density by zip code in Arlington VA. 
- Click on the zip code of choice to view projected crime occurrence for that region over a selected time frame. 
- Crime type can also be used as a filter to compare historical and forecasted density of different regions.

![image](https://github.com/a-memme/arlington_crime_density/assets/79600550/e8dc2631-9326-4986-a6c7-f5726d9aee32)

### Crime Density Timelapse 
- Use this tab to view how crime density trends have changed over time and space. 
- The timelapse feature can be used to view trends over different time aggregations (i.e yearly, monthly, day of week, etc trends)

![image](https://github.com/a-memme/arlington_crime_density/assets/79600550/65fd6c11-1ea1-4b2a-a000-18becfef18c0)


Enjoy visualizing!


## Summary of Files:
- Data Collection, Cleaning and Wrangling [data_cleaning/](https://github.com/a-memme/arlington_crime_density/tree/main/data_cleaning):
    - Navigate to this folder to view preliminary notebooks and datasets derived through the data collection and eda stages.
    - Core crime density data scraped from [Arlington County Daily Crime Report](https://www.arlingtonva.us/About-Arlington/Newsroom?dlv_ARL%20CL%20Public%20News%20Listing%20without%20Image=(dd_OC%20News%20Categories=Daily%20Crime%20Report))

- Analysis and Modeling [ml_files/](https://github.com/a-memme/arlington_crime_density/tree/main/ml_files)
    - Model training, evaluation and testing.

- App Code:
    - methods.py
    - app.py
