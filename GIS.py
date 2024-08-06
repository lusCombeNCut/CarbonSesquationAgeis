import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import Draw

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

# Create a folium map centered around the UK
m = folium.Map(location=[55.3781, -3.4360], zoom_start=6)

# Add existing carbon sources to the map
for _, row in gdf.iterrows():
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=f"Year: {row[year_column]}\nEmissions: {row[emission_column]} tons",
        tooltip=row[emission_column]
    ).add_to(m)

# Add Draw tool to the map to allow users to add points
draw = Draw()
draw.add_to(m)

# Add a JavaScript function to handle the drawing event
draw_handler_js = """
function(e) {
    var layer = e.layer;
    var user_point = [layer.getLatLng().lat, layer.getLatLng().lng];

    // Send the user point to the backend for distance calculation
    fetch('/calculate_distance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({user_point: user_point})
    })
    .then(response => response.json())
    .then(data => {
        // Add a popup to the user point with the distance information
        layer.bindPopup("Distance to nearest carbon source: " + data.distance.toFixed(2) + " km").openPopup();
    });
}
"""
m.add_child(folium.Element(f"""
<script>
var map = {m.get_name()};
map.on('draw:created', {draw_handler_js});
</script>
"""))

# Save the map to an HTML file
m.save('carbon_sources_map_with_user_points.html')
