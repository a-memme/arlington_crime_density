import pandas as pd
import json

import prophet
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from IPython.display import display

import folium
from folium.plugins import HeatMap, HeatMapWithTime

def read_data(csv_file):
    raw = pd.read_csv(csv_file)

    df = raw.copy()
    df['date_reported'] = pd.to_datetime(df['date_reported'])
    df['incident_date'] = pd.to_datetime(df['incident_date'])
    df['ZIP_Code'] = df['ZIP_Code'].astype('int').astype('str')

    return df

class ZipMap:
    def __init__(self, data):
        self.data = data
    
    def get_params(self):
        params = {'changepoint_prior_scale': 2.0572436973839325,
                'changepoint_range': 0.8372595709743088,
                'seasonality_prior_scale': 3.0669614906164115,
                'holidays_prior_scale': 5.944894747597239,
                'seasonality_mode': 'multiplicative',
                'weekly_seasonality': 7,
                'yearly_seasonality': 4}
        
        return params

    def prophet_forecast(self, params, zip_code, crime_cat, periods=12):
        """ 
        This function uses Facebook's Prophet time series forecasting algorithm to
        predict the number of crimes that will be committed in a given zip code.
        
        Inputs:
        - params: fb prophet model params selected via optuna (probabilistic) hyperparameter tuning.
        - zip_code: String representing the zip code for which the forecast will be made.
        - crime: High-level crime category we wish to forecast. Options are "all" (all categories), 1: Crimes Against Person; 
        2: Crimes Against Property; 3: Crimes Against Society.
        - periods: Number of periods (months) to forecast.
        
        Returns:
        - fig_forecast: Plotly figure object displaying the forecast.
        - fig_components: Plotly figure object displaying the forecast components.
        """
        # Initialize Prophet model
        # m = Prophet(changepoint_prior_scale=autoregressive_weight)
        m = Prophet(**params)
        
        # Prepare the DataFrame for Prophet
        #df_prophet = df.copy().rename(columns={"date_reported":"ds"})
        df_prophet = self.data.copy().rename(columns={"incident_date":"ds"})
        df_prophet.set_index("ds", inplace=True)
        # if crime == 'all':
        #     df_prophet = df_prophet
        # else:
        #     df_prophet = df_prophet[df_prophet['CategoryCode']==crime]

        monthly_crime_counts = df_prophet.groupby('ZIP_Code').resample('M').size()
        monthly_crime_counts = monthly_crime_counts.rename('y').reset_index()
        model_df = monthly_crime_counts[monthly_crime_counts['ZIP_Code'] == zip_code]
        
        # Fit the model
        m.fit(model_df)
        
        # Make future dataframe
        future = m.make_future_dataframe(periods=periods, freq='M')
        
        # Make predictions
        forecast = m.predict(future)
        
        # Plot forecast and components
        fig_forecast = plot_plotly(m, forecast)
        fig_forecast.update_layout(
            title={
        'text': f'{crime_cat} - Density for ZIP {zip_code}',
        'font': {'size': 20, 'color': 'black', 'family': 'Arial'}
                },
            #title=f'{crime_cat} - Density for ZIP {zip_code} (2016-Present)',
            xaxis_title='Year Month', 
            yaxis_title='Crime Density per Month'
        )

        fig_components = plot_components_plotly(m, forecast)
        
        return forecast, fig_forecast, fig_components
    
    def aggregate_zips(self):
        aggregate = {'id': 'count',
                'yearmonth': 'nunique'}

        zips = self.data.groupby(['ZIP_Code']).agg(aggregate).reset_index()
        zips['cpm'] = round(zips['id'] / zips['yearmonth'], 1)

        return zips
    
    def geojson_zips(self, geojson):
        with open(geojson, 'r') as jsonFile:
            geo_data = json.load(jsonFile)

        tmp = geo_data 

        geozips = []

        for i in range(len(tmp['features'])):
            if tmp['features'][i]['properties']['ZCTA5CE10'] in list(self.data['ZIP_Code'].unique()):
                geozips.append(tmp['features'][i])

        new_json = dict.fromkeys(['type','features'])
        new_json['type'] = 'FeatureCollection'
        new_json['features'] = geozips

        return new_json
    
    def create_map(self, df, geojson):

        map_object = folium.Map([38.876577, -77.109773], zoom_start = 12)

        cp = folium.Choropleth(geo_data=geojson, 
                            fill_opacity=0.6, 
                            line_opacity=0.7,
                            data = df,
                            key_on='feature.properties.ZCTA5CE10',
                            columns=['ZIP_Code', 'id'],
                            fill_color='YlOrRd',
                            legend_name='Crime Density by ZIP',
                            highlight=True
        ).add_to(map_object)

        zips_i = df.set_index('ZIP_Code')

        for s in cp.geojson.data['features']:
            s['properties']['total_crime'] = zips_i.loc[s['properties']['ZCTA5CE10'], 'id'].astype('str')
            s['properties']['crimes_per_month'] = zips_i.loc[s['properties']['ZCTA5CE10'], 'cpm'].astype('str')

        folium.GeoJsonTooltip(
            fields=["ZCTA5CE10", "total_crime", "crimes_per_month"],
            aliases=["Zip Code:", "Total Crimes:", "Avg Crimes/Month:"],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=1000
        ).add_to(cp.geojson)

        folium.LayerControl().add_to(map_object)

        return map_object

class TimeLapse():

    def __init__(self, data):
        self.data = data

    def year_month(self):
        #Make a copy
        df = self.data.copy()
        df = df.groupby(['year', 'month_num', 'yearmonth', 'Latitude', 'Longitude']).count()['id'].reset_index()

        #Create time index
        time_index = list(df.sort_values(['year', 'month_num'])['yearmonth'].unique())

        data_list = []

        for year in time_index:
            sample = df[df['yearmonth'].isin([year])]

            year_list = [[lat, long, counts] for lat, long, counts in zip(sample['Latitude'], sample['Longitude'], sample['id'])]

            data_list.append(year_list)

        return data_list, time_index
    
    def yearly(self):
        #Make a copy
        df = self.data.copy()
        df = df[df['incident_date']<= '2023-12-31']
        df = df.groupby(['year', 'Latitude', 'Longitude']).count()['id'].reset_index()

        #Create time index
        time_index = list(df.sort_values(['year'])['year'].unique())

        data_list = []

        for year in time_index:
            sample = df[df['year'].isin([year])]

            year_list = [[lat, long, counts] for lat, long, counts in zip(sample['Latitude'], sample['Longitude'], sample['id'])]

            data_list.append(year_list)

        return data_list, time_index

    def agg_month(self):
        #Make a copy
        df = self.data.copy()
        df = df.groupby(['monthname', 'month_num', 'Latitude', 'Longitude']).count()['id'].reset_index()

        # Create time index
        time_index = list(df.sort_values(['month_num'])['monthname'].unique())

        data_list = []

        for month in time_index:
            sample = df[df['monthname'].isin([month])]

            month_list = [[lat, long, counts] for lat, long, counts in zip(sample['Latitude'], sample['Longitude'], sample['id'])]

            data_list.append(month_list)

        return data_list, time_index

    def dow(self):
        #Make a copy
        df = self.data.copy()
        df = df.groupby(['dow', 'dow_num', 'Latitude', 'Longitude']).count()['id'].reset_index()

        #Create index
        time_index = list(df.sort_values(['dow_num'])['dow'].unique())

        data_list = []

        for dow in time_index:
            sample = df[df['dow'].isin([dow])]

            dow_list = [[lat, long, counts] for lat, long, counts in zip(sample['Latitude'], sample['Longitude'], sample['id'])]

            data_list.append(dow_list)

        return data_list, time_index

    def create_timelapse(self, data_list, time_index):
        map_object = folium.Map([38.876577, -77.109773], zoom_start = 12)

        hm = HeatMapWithTime(data=data_list,
                            index=time_index, 
                            radius=10, 
                            max_opacity=0.7)

        hm.add_to(map_object)
        
        return map_object