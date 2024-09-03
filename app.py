from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import requests

app = Flask(__name__)

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Weather Route
@app.route('/weather', methods=['POST'])
def weather():
    location_name = request.form.get('location')
    
    # Initialize Nominatim geocoder
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(location_name)

    # Handle case where location is not found
    if not location:
        return render_template('index.html', forecast_list=[], location_name=location_name, forecast="Location not found.")

    # Extract latitude and longitude from location
    latitude = location.latitude
    longitude = location.longitude

    grid_url = f"https://api.weather.gov/points/{latitude},{longitude}"
    grid_response = requests.get(grid_url)
    
    if grid_response.status_code == 200:
        grid_data = grid_response.json()
        grid_id = grid_data['properties']['gridId']
        grid_x = grid_data['properties']['gridX']
        grid_y = grid_data['properties']['gridY']
        
        forecast_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast"
        forecast_response = requests.get(forecast_url)
        
        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            periods = forecast_data['properties']['periods']
            
            forecast_list = []
            for period in periods[:7]:
                forecast_list.append({
                    "name": period['name'],
                    "temperature": period['temperature'],
                    "icon": period['icon'],
                    "detailedForecast": period['detailedForecast']
                })
            
            return render_template('index.html', forecast_list=forecast_list, location_name=location_name)
    
    return render_template('index.html', forecast_list=[], location_name=location_name, forecast="Error retrieving weather data.")



if __name__ == '__main__':
    app.run(debug=True)
