from flask import Flask, request, jsonify, send_from_directory
from geopy.distance import geodesic
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Initialize Flask app
app = Flask(__name__)

# Read the CSV file
file_path = 'csv-data.csv'
data = pd.read_csv(file_path)

# Correct column names
year_column = 'Year'
easting_column = 'Easting'
northing_column = 'Northing'
emission_column = 'Emission'

# Convert the easting and northing to a GeoDataFrame
gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data[easting_column], data[northing_column]),
    crs="EPSG:27700"  # British National Grid
)

# Convert to WGS84 (latitude and longitude)
gdf = gdf.to_crs(epsg=4326)

# Convert GeoDataFrame to a list of tuples for distance calculation
carbon_sources = [(row.geometry.y, row.geometry.x) for _, row in gdf.iterrows()]

def calculate_nearest_distance(user_point, carbon_sources):
    min_distance = float('inf')
    closest_source = None
    for source_point in carbon_sources:
        distance = geodesic(user_point, source_point).kilometers
        if distance < min_distance:
            min_distance = distance
            closest_source = source_point
    return min_distance, closest_source

@app.route('/')
def serve_map():
    return send_from_directory('', 'carbon_sources_map_with_user_points.html')

@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    user_point = request.json['user_point']
    min_distance, _ = calculate_nearest_distance(user_point, carbon_sources)
    return jsonify({'distance': min_distance})

if __name__ == '__main__':
    app.run(debug=True)
