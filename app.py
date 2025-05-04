import streamlit as st
import requests
import pandas as pd

st.title("Streamlit Charts!")
st.markdown("---")

st.header("Weather Forecast")
col1, col2 = st.columns(2)

with col1:
    lat = st.number_input("Latitude", value=7.19, format="%.2f")
with col2:
    lon = st.number_input("Longitude", value=125.45, format="%.2f")

if st.button("Get Weather Data"):
    try:
        BASE_URL = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode",
            "timezone": "auto",
            "past_days": 7 # Include last 7 days
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        st.success(f"Successfully fetched data for Latitude: {lat}, Longitude: {lon}")

        # Parse data into a DataFrame
        daily_data = data['daily']
        df_weather = pd.DataFrame(daily_data)

        # Convert time column to datetime and set as index (important for st charts)
        df_weather['time'] = pd.to_datetime(df_weather['time'])
        df_weather.set_index('time', inplace=True)

        # Display results
        st.subheader("Weather Overview (Next 7 Days + Past 7 Days)")

        # 1. Metrics
        latest_day = df_weather.index[-1]
        st.metric("Latest Max Temp (°C)", f"{df_weather.loc[latest_day, 'temperature_2m_max']:.1f}")
        st.metric("Latest Min Temp (°C)", f"{df_weather.loc[latest_day, 'temperature_2m_min']:.1f}")
        st.metric("Latest Precipitation (mm)", f"{df_weather.loc[latest_day, 'precipitation_sum']:.1f}")

        st.markdown("---")
        st.subheader("Charts")

        # 2. Line Chart (Temperatures)
        st.write("Temperature")
        st.line_chart(df_weather[['temperature_2m_max', 'temperature_2m_min']])

        # 3. Bar Chart (Precipitation)
        st.write("Precipitation")
        st.bar_chart(df_weather['precipitation_sum'])

        # 4. Area Chart (Wind Speed)
        st.write("Wind Speed")
        st.area_chart(df_weather['windspeed_10m_max'])

        # 5. Scatter Chart (Temp Max vs Precipitation) - Might not be super insightful but demonstrates the chart
        st.write("Temperature vs Precipitation")
        st.scatter_chart(df_weather, x='temperature_2m_max', y='precipitation_sum')

        # 6. Data Table (Counts as a display type)
        st.subheader("Raw Daily Data")
        st.dataframe(df_weather)

    except requests.exceptions.RequestException as e:
        st.error(f"API Request Failed: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.markdown("---")